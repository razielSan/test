from typing import Union, Dict, Any
from dataclasses import dataclass

from core.constants.error import DefaultError


@dataclass(frozen=True)
class ErrorResponse:
    code: str
    message: str


DEFAULT_ERROR = ErrorResponse(
    code=DefaultError.code,
    message=DefaultError.message,
)


def format_error_messages(
    method: str,
    url: str,
    code: str,
    message: str,
    context: Dict[str, Any],
) -> str:
    """
    Приводит данные к единому формату и возращает строку

    >>> format_error_messages(
    ... "POST",
    ... "https://example.com",
    ... "A user with that name already exists",
    ... "USER ALREADY EXISTS",
    ... {"detail": "Some details"}) # doctest: +NORMALIZE_WHITESPACE
    "POST https://example.com A user with that name already exists
    USER ALREADY EXISTS {'detail': 'Some details'}"
    """

    return "%s %s %s %s %s" % (method, url, code, message, context)


class AppException(Exception):
    def __init__(
        self,
        error: ErrorResponse = DEFAULT_ERROR,
        status_code: int = 500,
        **context: Union[str, int],
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.context = context


class UserAlreadyExists(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=409,
            error=ErrorResponse(
                code="USER ALREADY EXISTS",
                message="A user with that name already exists",
            ),
            **context,
        )


class UserNotFound(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=409,
            error=ErrorResponse(
                code="USER NOT FOUND",
                message="A user with that name was not found.",
            ),
            **context,
        )


class IncorrectPassword(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=409,
            error=ErrorResponse(
                code="INCORRECT PASSWORD",
                message="The password was entered incorrectly",
            ),
            **context,
        )


class AuthenticatedError(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=409,
            error=ErrorResponse(
                code="AUTHENTICATED ERROR",
                message="The password or username was entered incorrectly",
            ),
            **context,
        )


class AdminDoesNotInizialized(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=409,
            error=ErrorResponse(
                code="ADMIN DOESN'T INITIALIZED",
                message="The admin has not been initialized",
            ),
            **context,
        )


class NameDoesNotExists(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=409,
            error=ErrorResponse(
                code="NAME DOESN'T EXISTS",
                message="The name does not exists",
            ),
            **context,
        )


class TableDoesNotExists(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=409,
            error=ErrorResponse(
                code="TABLE DOESN'T EXISTS",
                message="The table does not exists",
            ),
            **context,
        )


class InvalidToken(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=401,
            error=ErrorResponse(
                code="INVALID TOKEN",
                message="Invalid token",
            ),
            **context,
        )


class TokenExpired(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=401,
            error=ErrorResponse(
                code="TOKEN EXPIRED",
                message="Token has expired",
            ),
            **context,
        )


class AdminAccessRequired(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=403,
            error=ErrorResponse(
                code="ROLE MISMATCH",
                message="Admin access required",
            ),
            **context,
        )


class UnauthorizedError(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=401,
            error=ErrorResponse(
                code="USER UNAUTHORIZED",
                message="User is not authorized",
            ),
            **context,
        )


class OriginError(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=403,
            error=ErrorResponse(
                code="ORIGIN ERROR",
                message="Request origin is not allowed",
            ),
            **context,
        )


class RefererError(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=403,
            error=ErrorResponse(
                code="REFERER ERROR",
                message="Request origin is not allowed",
            ),
            **context,
        )


class RateLimitError(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=429,
            error=ErrorResponse(
                code="RATE LIMIT ERROR",
                message="The number of allowed login"
                " attempts has been exceeded.Please try again later.",
            ),
            **context,
        )


class IpNotFoundError(AppException):
    def __init__(
        self,
        **context: Union[str, int],
    ) -> None:
        super().__init__(
            status_code=500,
            error=ErrorResponse(code="IP NOT FOUND", message="Unable to determine client IP"),
            **context,
        )
