from typing import Tuple
from logging import Logger

from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from app.my_project.backend.presentation.extensions import templates
from app.my_project.backend.application.api.cookies import CookieApiProtocol
from app.my_project.backend.presentation.dependencies import (
    get_current_user,
    get_cookie_api,
    get_jwt_security,
    get_allowed_redirect_urls,
    get_logger,
)
from app.my_project.backend.presentation.url import PageUrl, ErrorUrl
from domain.exceptions import InvalidToken, TokenExpired, format_error_messages
from core.constants.user import TokenName
from core.constants.error import (
    RedirectUrlNotAllowedError,
    NextMissingError,
    RefreshTokenMissingError,
)
from infrastructure.security.token import JWTSecurityProtocol


router = APIRouter()


@router.get(PageUrl.MAIN_PAGE)
async def main_page(
    request: Request,
) -> HTMLResponse:
    response = templates.TemplateResponse(
        request=request,
        name="pages/index.html",
    )
    return response


@router.get(
    PageUrl.USER_PAGE,
    dependencies=[Depends(get_current_user)],
)
async def user_page(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="pages/user.html",
    )


@router.get(
    path=PageUrl.REFRESH_PAGE,
)
async def update_access_token_by_page(
    request: Request,
    cookie_api: CookieApiProtocol = Depends(get_cookie_api),
    jwt_security: JWTSecurityProtocol = Depends(get_jwt_security),
    allowed_redirect_urls: Tuple[str, ...] = Depends(get_allowed_redirect_urls),
    logger: Logger = Depends(get_logger),
) -> Response:
    # проверка на наличие next
    next_url = request.query_params.get("next")
    if not next_url:
        logger.warning(
            format_error_messages(
                method=request.method,
                url=request.url.path,
                code=NextMissingError.code,
                message=NextMissingError.message,
                context={},
            )
        )
        return RedirectResponse(
            url=PageUrl.MAIN_PAGE,
            status_code=NextMissingError.status_code,
        )
    if next_url not in allowed_redirect_urls:
        logger.warning(
            format_error_messages(
                method=request.method,
                url=request.url.path,
                code=RedirectUrlNotAllowedError.code,
                message=RedirectUrlNotAllowedError.message % next_url,
                context={},
            )
        )
        response_next_url = templates.TemplateResponse(
            request=request,
            name=ErrorUrl.FORBIDDEN,
            status_code=RedirectUrlNotAllowedError.status_code,
        )

        cookie_api.delete_cookie(
            token_name=TokenName.ACCESS_TOKEN.value,
            response=response_next_url,
        )
        cookie_api.delete_cookie(
            token_name=TokenName.REFRESH_TOKEN.value,
            response=response_next_url,
        )
        return response_next_url

    refresh_token = request.cookies.get(TokenName.REFRESH_TOKEN.value)
    if not refresh_token:
        logger.warning(
            format_error_messages(
                method=request.method,
                url=request.url.path,
                code=RefreshTokenMissingError.code,
                message=RefreshTokenMissingError.message,
                context={},
            )
        )
        return RedirectResponse(
            url=PageUrl.MAIN_PAGE,
            status_code=RefreshTokenMissingError.status_code,
        )
    try:
        payload = jwt_security.decode_refresh_token(token=refresh_token)
        access_token = jwt_security.create_access_token(user_id=payload.sub)
    except (TokenExpired, InvalidToken) as exc:
        logger.warning(
            format_error_messages(
                method=request.method,
                url=request.url.path,
                code=exc.error.code,
                message=exc.error.message,
                context=exc.context,
            )
        )
        response = templates.TemplateResponse(
            request=request,
            name=ErrorUrl.SESSION_EXPIRED,
            status_code=exc.status_code,
        )
        cookie_api.delete_cookie(
            token_name=TokenName.ACCESS_TOKEN.value,
            response=response,
        )
        cookie_api.delete_cookie(
            token_name=TokenName.REFRESH_TOKEN.value,
            response=response,
        )
        return response

    redirect_response = RedirectResponse(
        url=next_url,
        status_code=303,
    )
    cookie_api.set_auth_cookies(
        response=redirect_response,
        access_token=access_token,
    )
    return redirect_response
