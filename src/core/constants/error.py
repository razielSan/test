from enum import Enum


class ErrorCode(str, Enum):  # error codes, not secrets of the application
    VALIDATION_ERROR = "VALIDATION ERROR"
    UNKNOWN_ERROR = "UNKNOWN ERROR"
    REDIRECT_URL_NOT_ALLOWED = "REDIRECT URL NOT ALLOWED"
    NEXT_MISSING = "NEXT MISSING"
    REFRESH_TOKEN_MISSING = "REFRESH TOKEN MISSING"  # nosec B105
    INVALID_DATABASE_URL = "INVALID DATABASE URL"
    DRIVER_NOT_SUPPORTED = "DRIVER NOT SUPPORTED"
    DATABASE_NAME_NOT_SUPPORTED = "DATABASE NAME NOT SUPPORTED"
    DRIVER_NOT_SUPPORTED_DATABASE = "DRIVER NOT SUPPORTED DATABASe"
    DATABASE_CONFIGURATION_ERROR = "DATABASE CONFIGURATION ERROR"


class DigitNotFoundError:
    message: str = "The password must contain at least 1 digit"
    code: str = ErrorCode.VALIDATION_ERROR.value


class LetterNotFoundError:
    message: str = "The password must contain at least 1 letter"
    code: str = ErrorCode.VALIDATION_ERROR.value


class DefaultError:
    code: str = ErrorCode.UNKNOWN_ERROR.value
    message: str = "An unknown error has occurred,please try making the request again"


class InvalidDatabaseUrl:
    code: str = ErrorCode.INVALID_DATABASE_URL.value
    message: str = "Invalid database url - %s\n-----\nExample correct url: %s\n-----"


class DriverNotSupported:
    code: str = ErrorCode.DRIVER_NOT_SUPPORTED.value
    message: str = "Driver not supported - %s\n-----\nSupported drivers: %s\n-----"


class DatabaseNameNotSupported:
    code: str = ErrorCode.DATABASE_NAME_NOT_SUPPORTED.value
    message: str = "Database name not supported - %s\n-----\nSupported databases: %s\n-----"


class DriverNotSupportedDatabase:
    code: str = ErrorCode.DRIVER_NOT_SUPPORTED_DATABASE.value
    message: str = (
        "Driver not in supported database" " - %s\n-----\nSupported drivers by database: %s\n-----"
    )


class DatabaseConfigurationError:
    code: str = ErrorCode.DATABASE_CONFIGURATION_ERROR.value
    message: str = "The database URL or settings are configured incorrectly."


class RedirectUrlNotAllowedError:
    status_code: int = 401
    message: str = "Redirect URL is not allowed: %s"
    code: str = ErrorCode.REDIRECT_URL_NOT_ALLOWED.value


class NextMissingError:
    status_code: int = 303
    message: str = "Request does not contain next URL"
    code: str = ErrorCode.NEXT_MISSING.value


class RefreshTokenMissingError:
    status_code: int = 303
    message: str = "Refresh token is missing"
    code: str = ErrorCode.REFRESH_TOKEN_MISSING.value
