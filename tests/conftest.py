import asyncio
import sys
import logging
from datetime import timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.my_project.backend.presentation.url import ALLOWED_REDIRECT_URLS
from app.my_project.backend.application.api.cookies import CookieApi
from app.my_project.backend.presentation.url import PageUrl
from app.my_project.backend.presentation.dependencies import (
    get_allowed_origins,
    get_uow,
    get_rate_limit_service,
)
from infrastructure.db.redis.rate_limit import RateLimitRedisClient
from infrastructure.security.token import PyJWTSecurity
from test_data.db.redis import RateLimiTestService
from test_data.utils import get_backends
from test_data.settings import test_settings
from test_data.constants import (
    TEST_ALLOWED_ORIGINS,
    TEST_TRUSTED_PROXIES,
    IpClientTest,
    AppStorageTest,
)


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def pytest_addoption(parser):
    parser.addoption(
        "--backend",
        action="store",
        default=test_settings.SQLITE_NAME_DATABASE,
    )


@pytest.fixture(scope="session")
def logger():
    logger = logging.getLogger(name=__name__)
    return logger


@pytest.fixture()
def test_trusted_proxies():
    return TEST_TRUSTED_PROXIES


@pytest_asyncio.fixture(scope="session")
async def backend(request):
    database_name = request.config.getoption("--backend")

    backend = get_backends(
        type_database=database_name,
    )
    await backend.create_tables()
    await backend.create_defaults_roles()
    yield backend
    if hasattr(backend, "delete_database"):
        await backend.delete_database()


@pytest_asyncio.fixture(scope="session")
async def test_rate_limit_service(
    logger,
) -> RateLimiTestService:
    rate_limiter = RateLimitRedisClient()
    rate_limite_service = RateLimiTestService(
        time_limit=1,
        max_name_counter=5,
        max_ip_counter=5,
        rate_limiter=rate_limiter,
        logger=logger,
    )
    return rate_limite_service


@pytest_asyncio.fixture
async def test_uow(
    backend,
):
    try:
        yield backend.get_uow()
    finally:
        await backend.cleare_database()


def pytest_sessionfinish(session, exitstatus):
    database_name = session.config.getoption("--backend")

    print(f"\nTest database - {database_name}")


@pytest_asyncio.fixture
async def app_storage(
    test_rate_limit_service,
    test_uow,
):
    app.dependency_overrides[get_uow] = lambda: test_uow
    app.dependency_overrides[get_allowed_origins] = lambda: TEST_ALLOWED_ORIGINS
    app.state.allowed_redirect_urls = ALLOWED_REDIRECT_URLS
    app.state.trusted_proxies = TEST_TRUSTED_PROXIES
    app.dependency_overrides[get_rate_limit_service] = lambda: test_rate_limit_service
    app.state.cookie_api = CookieApi(
        httponly=True, samesite="lax", secure=False, path=PageUrl.MAIN_PAGE
    )
    app.state.jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=15),
        refresh_token_lifetime=timedelta(days=7),
    )
    transport = ASGITransport(
        app=app,
        client=(
            IpClientTest.host.value,
            int(IpClientTest.port.value),
        ),
    )
    async with AsyncClient(transport=transport, base_url=TEST_ALLOWED_ORIGINS[0]) as client:
        client.headers = {"Origin": TEST_ALLOWED_ORIGINS[0]}
        yield AppStorageTest(
            client=client,
            app=app,
        )
    app.dependency_overrides.clear()
