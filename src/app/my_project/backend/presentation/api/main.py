from typing import Dict
from logging import Logger

from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.my_project.backend.presentation.dependencies import (
    get_uow,
    get_hasher,
    get_auth_service,
    get_current_user,
    verify_origin,
    get_rate_limit_service,
    get_cookie_api,
    get_user_ip,
    get_jwt_security,
    get_logger,
)
from app.my_project.backend.application.user.create_user import CreateUser
from app.my_project.backend.application.user.authenticate_user import (
    AuthenticateUser,
)
from app.my_project.backend.application.user.delete_user import DeleteUser
from app.my_project.backend.application.user.update_user import (
    UpdateUserPassword,
    UpdateUserName,
)
from app.my_project.backend.application.services.authentication import (
    AuthenticationServiceProtocol,
)
from app.my_project.backend.application.api.cookies import CookieApiProtocol
from app.my_project.backend.application.services.rate_limit import (
    RateLimitServiceProtocol,
)
from app.my_project.backend.presentation.url import ApiMainUrl
from dto.user import (
    CreateUserDTO,
    UserDTO,
    UpdateUserPasswordDTO,
    UpdateUserNameDTO,
    AuthenticateUserDTO,
)
from domain.db.base import UnitOfWorkProtocol
from domain.exceptions import AuthenticatedError, format_error_messages
from domain.security.hasher import PasswordHasherProtocol
from infrastructure.security.token import (
    JWTSecurityProtocol,
    set_auth_user_by_tokens_and_cookies,
)
from core.constants.user import ResponseMessageUser, TokenName
from core.constants.error import RefreshTokenMissingError


router = APIRouter(
    tags=["user"],
    prefix=ApiMainUrl.PREFIX,
)


@router.post(
    path=ApiMainUrl.REGISTER_USER,
    response_model=UserDTO,
    dependencies=[Depends(verify_origin)],
)
async def register_user(
    response: Response,
    user: CreateUserDTO,
    uow: UnitOfWorkProtocol = Depends(get_uow),
    hasher: PasswordHasherProtocol = Depends(get_hasher),
    cookie_api: CookieApiProtocol = Depends(get_cookie_api),
    jwt_security: JWTSecurityProtocol = Depends(get_jwt_security),
) -> UserDTO:
    created_user = await CreateUser(uow=uow, hasher=hasher).execute(
        user=user,
    )
    set_auth_user_by_tokens_and_cookies(
        cookie_api=cookie_api,
        user_id=str(created_user.id),
        response=response,
        jwt_security=jwt_security,
    )
    return created_user


@router.post(
    path=ApiMainUrl.AUTHENTICATE_USER,
    dependencies=[
        Depends(verify_origin),
    ],
)
async def authenticate_user(
    response: Response,
    user_ip: str = Depends(get_user_ip),
    rate_limite_service: RateLimitServiceProtocol = Depends(
        get_rate_limit_service,
    ),
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow: UnitOfWorkProtocol = Depends(get_uow),
    auth_service: AuthenticationServiceProtocol = Depends(get_auth_service),
    cookie_api: CookieApiProtocol = Depends(get_cookie_api),
    jwt_securtiy: JWTSecurityProtocol = Depends(get_jwt_security),
) -> Response:
    await rate_limite_service.check_login(
        ip=user_ip,
        name=form_data.username,
    )

    try:
        authenticated_user = await AuthenticateUser(
            uow=uow,
            auth_service=auth_service,
        ).execute(
            user=AuthenticateUserDTO(
                password=form_data.password,
                username=form_data.username,
            ),
        )
    except AuthenticatedError as err:
        # Если пользователь ввел неправильные даныые повышаем счетчики количества попыток
        attempt_counter = await rate_limite_service.increase_the_attempt_counter(
            ip=user_ip,
            name=form_data.username,
        )
        # устнанавливаем лимит по времени для счетчиков если они равны 1
        await rate_limite_service.setting_time_limit(
            ip=user_ip,
            name=form_data.username,
            attempt_counter=attempt_counter,
        )

        raise AuthenticatedError() from err

    set_auth_user_by_tokens_and_cookies(
        cookie_api=cookie_api,
        user_id=str(authenticated_user.id),
        response=response,
        jwt_security=jwt_securtiy,
    )

    response.status_code = 204
    return response


@router.post(
    path=ApiMainUrl.REFRESH,
    dependencies=[Depends(verify_origin)],
)
async def update_access_token(
    request: Request,
    response: Response,
    cookie_api: CookieApiProtocol = Depends(get_cookie_api),
    jwt_security: JWTSecurityProtocol = Depends(get_jwt_security),
    logger: Logger = Depends(get_logger),
) -> Dict[str, str]:
    refresh_token = request.cookies.get(TokenName.REFRESH_TOKEN.value)
    if not refresh_token:
        logger.warning(
            format_error_messages(
                method=request.method,
                url=request.url.path,
                message=RefreshTokenMissingError.message,
                code=RefreshTokenMissingError.code,
                context={},
            )
        )
        return ResponseMessageUser.NOT_AUTHTENTICATE

    payload = jwt_security.decode_refresh_token(token=refresh_token)
    access_token = jwt_security.create_access_token(
        user_id=payload.sub,
    )

    cookie_api.set_auth_cookies(
        response=response,
        access_token=access_token,
    )
    return ResponseMessageUser.UPDATE_ACCESS_TOKEN_SUCCESS


@router.delete(
    path=ApiMainUrl.DELETE_USER,
    response_model=UserDTO,
    dependencies=[Depends(verify_origin)],
)
async def delete_user(
    uow: UnitOfWorkProtocol = Depends(get_uow),
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    deleted_user = await DeleteUser(
        uow=uow,
    ).execute(user=current_user)
    return deleted_user


@router.patch(
    path=ApiMainUrl.UPDATE_USER_PASSWORD,
    response_model=UserDTO,
    dependencies=[Depends(verify_origin)],
)
async def update_user_password(
    user: UpdateUserPasswordDTO,
    uow: UnitOfWorkProtocol = Depends(get_uow),
    current_user: UserDTO = Depends(get_current_user),
    auth_service: AuthenticationServiceProtocol = Depends(get_auth_service),
) -> UserDTO:
    updated_user = await UpdateUserPassword(
        uow=uow,
        auth_service=auth_service,
    ).execute(
        user=user,
        user_id=current_user.id,
    )
    return updated_user


@router.patch(
    path=ApiMainUrl.UPDATE_USERNAME,
    response_model=UserDTO,
    dependencies=[Depends(verify_origin)],
)
async def update_username(
    user: UpdateUserNameDTO,
    uow: UnitOfWorkProtocol = Depends(get_uow),
    current_user: UserDTO = Depends(get_current_user),
    auth_service: AuthenticationServiceProtocol = Depends(get_auth_service),
) -> UserDTO:
    updated_user = await UpdateUserName(
        uow=uow,
        auth_service=auth_service,
    ).execute(
        user=user,
        user_id=current_user.id,
    )
    return updated_user


@router.get(path=ApiMainUrl.GET_USER)
async def get_user(
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    return current_user


@router.post(path=ApiMainUrl.LOGOUT_USER, dependencies=[Depends(verify_origin)])
async def logout_user(
    response: Response, cookie_api: CookieApiProtocol = Depends(get_cookie_api)
) -> Dict[str, str]:
    cookie_api.delete_cookie(
        token_name=TokenName.ACCESS_TOKEN.value,
        response=response,
    )
    cookie_api.delete_cookie(token_name=TokenName.REFRESH_TOKEN.value, response=response)

    return ResponseMessageUser.LOGOUT_SUCCESS
