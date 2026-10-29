import logging
from datetime import timedelta
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from socket import gaierror

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import ArgumentError, OperationalError

from app.my_project.backend.core.routers import inculde_routers
from app.my_project.backend.core.middleware import (
    SecurityMiddleware,
)
from app.my_project.backend.settings.paths import STATIC_DIR
from app.my_project.backend.presentation.url import PageUrl, ALLOWED_REDIRECT_URLS
from app.my_project.backend.presentation.constants import TRUSTED_PROXIES
from app.my_project.backend.presentation.pages import main_router
from app.my_project.backend.application.api.cookies import CookieApi
from app.my_project.backend.application.services.rate_limit import RateLimitService
from app.my_project.backend.presentation.api import api_main_router, api_admin_router
from app.my_project.backend.core.exceptions import include_exceptions
from domain.db.utils import validate_database_name_and_driver
from core.log.logging import setup_loggers
from core.constants.error import DatabaseConfigurationError
from infrastructure.db.settings import DatabaseConfig
from infrastructure.security.token import PyJWTSecurity
from infrastructure.db.redis.rate_limit import RateLimitRedisClient
from infrastructure.security.url import ALLOWED_ORIGINS
from settings.config import settings


def create_up() -> FastAPI:
    validate_database_name_and_driver(url=settings.DATABASE_CONNECT)

    setup_loggers()
    logger = logging.getLogger(name=__name__)
    logger.info(settings.SECRET_KEY_TOKEN)

    @asynccontextmanager
    async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
        try:
            database_config = DatabaseConfig(
                logger=logger,
                database_url=settings.DATABASE_CONNECT,
            )
            await database_config.check_database()
            await database_config.check_required_roles()
            await database_config.check_admin_exists()
            logger.info("The admin has been successfully initialized")

            cookie_api = CookieApi(
                httponly=True,
                samesite="lax",
                secure=False,
                path=PageUrl.MAIN_PAGE,
            )
            jwt_security = PyJWTSecurity(
                access_token_lifetime=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                refresh_token_lifetime=timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
                ),
            )

            app.state.uow = database_config.uow
            app.state.cookie_api = cookie_api
            app.state.allowed_origins = ALLOWED_ORIGINS
            app.state.trusted_proxies = TRUSTED_PROXIES
            app.state.allowed_redirect_urls = ALLOWED_REDIRECT_URLS
            app.state.jwt_security = jwt_security
        except ArgumentError:
            logger.exception(DatabaseConfigurationError.message)
            raise
        except OperationalError:
            logger.exception(DatabaseConfigurationError.message)
            raise
        except gaierror:
            logger.exception(DatabaseConfigurationError.message)
            raise
        except UnicodeError:
            logger.exception(DatabaseConfigurationError.message)
            raise
        except Exception:
            logger.exception(DatabaseConfigurationError.message)
            raise

        rate_limiter = RateLimitRedisClient()
        rate_limit_service = RateLimitService(
            time_limit=60,
            max_name_counter=5,
            max_ip_counter=5,
            rate_limiter=rate_limiter,
            logger=logger,
        )
        app.state.rate_limit_service = rate_limit_service
        try:
            yield
        finally:
            await rate_limiter.close_connection()

    app = FastAPI(lifespan=life_span)
    app.state.logger = logger
    logger.info("Session connected")

    app.mount(path="/static", app=StaticFiles(directory=STATIC_DIR), name="static")
    logger.info("Static connected")

    app.add_middleware(SecurityMiddleware)
    logger.info("Middleware connected")

    inculde_routers(
        app=app,
        logger=logger,
        routers={
            "main_router": main_router,
            "api_main_router": api_main_router,
            "api_admin_router": api_admin_router,
        },
    )
    include_exceptions(app=app, logger=logger)
    return app
