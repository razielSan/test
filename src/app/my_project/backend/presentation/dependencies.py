from typing import Tuple
from logging import Logger

from fastapi import Request, Depends

from app.my_project.backend.application.services.authentication import (
    AuthenticationService,
    AuthenticationServiceProtocol,
)
from app.my_project.backend.application.api.cookies import CookieApiProtocol
from app.my_project.backend.application.services.rate_limit import (
    RateLimitServiceProtocol,
)
from app.my_project.backend.application.user.get_user import GetUser
from domain.exceptions import (
    AdminAccessRequired,
    UnauthorizedError,
    OriginError,
    RefererError,
    IpNotFoundError,
)
from domain.security.hasher import PasswordHasherProtocol
from domain.db.base import UnitOfWorkProtocol
from domain.db.constants import Role
from dto.user import UserDTO
from infrastructure.security.hash import ArgonHasher
from infrastructure.security.token import JWTSecurityProtocol
from infrastructure.security.url import SAFE_METHODS, get_origin_from_referer


async def get_uow(request: Request) -> UnitOfWorkProtocol:
    uow: UnitOfWorkProtocol = request.app.state.uow
    return uow


def get_hasher() -> PasswordHasherProtocol:
    return ArgonHasher()


def get_trusted_proxies(request: Request) -> Tuple[str, ...]:
    proxies: Tuple[str, ...] = request.app.state.trusted_proxies
    return proxies


def get_user_ip(
    request: Request,
    trusted_proxies: Tuple[str, ...] = Depends(get_trusted_proxies),
) -> str:
    client_ip = None
    if request.client is not None:
        client_ip = request.client.host

    if client_ip in trusted_proxies:
        forwared_for = request.headers.get("X-Forwarded-For")
        if forwared_for:
            return forwared_for.split(",")[0].strip()
    if client_ip:
        return client_ip
    raise IpNotFoundError(
        client=str(client_ip),
        user_agent=request.headers.get("user-agent", "unknown"),
        content_type=request.headers.get("content-type", "unknown"),
        origin=request.headers.get("origin", "unknown"),
        referer=request.headers.get("referer", "unknown"),
        accept_encoding=request.headers.get("accept-encoding", "unknown"),
        accept_language=request.headers.get("accept-language", "unknown"),
    )


def get_cookie_api(request: Request) -> CookieApiProtocol:
    cookie_api: CookieApiProtocol = request.app.state.cookie_api
    return cookie_api


def get_jwt_security(request: Request) -> JWTSecurityProtocol:
    jwt_security: JWTSecurityProtocol = request.app.state.jwt_security
    return jwt_security


def get_rate_limit_service(request: Request) -> RateLimitServiceProtocol:
    rate_limit_service: RateLimitServiceProtocol = request.app.state.rate_limit_service
    return rate_limit_service


def get_allowed_origins(request: Request) -> Tuple[str, ...]:
    allowed_origins: Tuple[str, ...] = request.app.state.allowed_origins
    return allowed_origins


def get_auth_service(
    request: Request,
    hasher: PasswordHasherProtocol = Depends(get_hasher),
) -> AuthenticationServiceProtocol:
    logger = request.app.state.logger
    return AuthenticationService(
        hasher=hasher,
        logger=logger,
    )


def get_allowed_redirect_urls(
    request: Request,
) -> Tuple[str, ...]:
    redirect_uls: Tuple[str, ...] = request.app.state.allowed_redirect_urls
    return redirect_uls


def get_logger(request: Request) -> Logger:
    logger: Logger = request.app.state.logger
    return logger


async def get_current_user(
    request: Request,
    uow: UnitOfWorkProtocol = Depends(get_uow),
    jwt_security: JWTSecurityProtocol = Depends(get_jwt_security),
) -> UserDTO:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise UnauthorizedError()
    payload = jwt_security.decode_access_token(token=access_token)
    try:
        user_id = int(payload.sub)
    except (ValueError, TypeError) as err:
        raise UnauthorizedError() from err

    user = await GetUser(uow=uow).execute(user_id=user_id)

    if not user.is_active:
        raise UnauthorizedError()
    return user


async def verify_origin(
    request: Request,
    allowed_origins: Tuple[str, ...] = Depends(get_allowed_origins),
) -> None:
    if request.method in SAFE_METHODS:
        return
    origin = request.headers.get("origin")
    if origin:
        if origin not in allowed_origins:
            raise OriginError()
        return

    referer = request.headers.get("referer")
    if not referer:
        raise RefererError()
    referer_origin = get_origin_from_referer(referer)
    if referer_origin is None or referer_origin not in allowed_origins:
        raise RefererError()


async def require_admin(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    async with uow as uow:
        roles = await uow.user_role.get_roles(user_id=current_user.id)

    if not any(role.name == Role.admin.value for role in roles):
        raise AdminAccessRequired()
    return current_user
