from logging import Logger
from urllib.parse import urlencode

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


from app.my_project.backend.presentation.errors import (
    format_validation_errors,
    is_api_request,
)
from app.my_project.backend.presentation.extensions import templates
from app.my_project.backend.presentation.url import PageUrl, ErrorUrl
from domain.exceptions import (
    AppException,
    UnauthorizedError,
    TokenExpired,
    format_error_messages,
)
from dto.exceptions import (
    AppExceptionDTO,
    ValidationErrorDTO,
    UnknownExceptionDTO,
    NotFoundPageDTO,
)


def include_exceptions(app: FastAPI, logger: Logger) -> None:
    @app.exception_handler(RequestValidationError)
    async def get_exception_validation_pydantic(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        error = ValidationErrorDTO(
            message=format_validation_errors(
                exc.errors(),
            )
        )
        return JSONResponse(
            status_code=error.status_code,
            content=error.content,
        )

    logger.info(f"Обработчик ошибок {RequestValidationError.__name__} подключен")

    @app.exception_handler(AppException)
    async def get_application_exceptions(
        request: Request,
        exc: AppException,
    ) -> Response:
        logger.warning(
            format_error_messages(
                method=request.method,
                url=request.url.path,
                code=exc.error.code,
                message=exc.error.message,
                context=exc.context,
            )
        )

        error = AppExceptionDTO(
            status_code=exc.status_code,
            code=exc.error.code,
            message=exc.error.message,
        )
        if is_api_request(request=request):
            return JSONResponse(
                status_code=error.status_code,
                content=error.content,
            )

        if isinstance(exc, UnauthorizedError):
            return RedirectResponse(
                url=PageUrl.MAIN_PAGE,
                status_code=303,
            )

        if isinstance(exc, TokenExpired):
            next_url = urlencode({"next": request.url.path})
            return RedirectResponse(
                url=f"{PageUrl.REFRESH_PAGE}?{next_url}",
                status_code=303,
            )

        return templates.TemplateResponse(
            request=request,
            name=ErrorUrl.INTERNAL_SERVER,
            status_code=error.status_code,
        )

    logger.info(f"Обработчик ошибок {AppException.__name__} подключен")

    @app.exception_handler(Exception)
    async def get_exception(request: Request, exc: Exception) -> Response:
        error = UnknownExceptionDTO()
        logger.exception(
            format_error_messages(
                method=request.method,
                url=request.url.path,
                code=error.content.get("code", "unknown"),
                message=error.content.get("message", "unknown"),
                context={},
            )
        )
        if is_api_request(request=request):
            return JSONResponse(
                status_code=error.status_code,
                content=error.content,
            )
        return templates.TemplateResponse(
            request=request,
            name=ErrorUrl.INTERNAL_SERVER,
            status_code=error.status_code,
        )

    logger.info("Обработчик ошибок Exception подключен")

    @app.exception_handler(404)
    async def handler_not_found(
        request: Request,
        exc: StarletteHTTPException,
    ) -> Response:
        not_found_exception = NotFoundPageDTO()
        logger.warning(
            format_error_messages(
                method=request.method,
                url=request.url.path,
                code=not_found_exception.content.get("code", "unknown"),
                message=not_found_exception.content.get("message", "unknown"),
                context={},
            )
        )
        if is_api_request(request=request):
            return JSONResponse(
                status_code=not_found_exception.status_code,
                content=not_found_exception.content,
            )
        return templates.TemplateResponse(
            request=request,
            name=ErrorUrl.NOT_FOUND,
            status_code=not_found_exception.status_code,
        )

    logger.info("Обработчик ошибки 404 подключен")
