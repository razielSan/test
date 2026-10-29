class ApiMainUrl:
    PREFIX: str = "/api"
    REGISTER_USER: str = "/auth/register"
    AUTHENTICATE_USER: str = "/auth/login"
    REFRESH: str = "/auth/refresh"
    DELETE_USER: str = "/users/me"
    UPDATE_USER_PASSWORD: str = "/users/password/me"
    UPDATE_USERNAME: str = "/users/username/me"
    GET_USER: str = "/users/me"
    LOGOUT_USER: str = "/auth/logout"


class PageUrl:
    MAIN_PAGE: str = "/"
    REFRESH_PAGE: str = "/auth/refresh"
    USER_PAGE: str = "/user"


class ErrorUrl:
    NOT_FOUND: str = "/pages/error/not_found.html"
    INTERNAL_SERVER: str = "/pages/error/internal_server.html"
    SESSION_EXPIRED: str = "/pages/error/session_expired.html"
    FORBIDDEN: str = "/pages/error/forbidden.html"


class ApiAdminUrl:
    PREFIX: str = "/api/admin"
    ADMIN_GET_USER: str = "/users/{user_id}"


ALLOWED_REDIRECT_URLS = (PageUrl.MAIN_PAGE, PageUrl.USER_PAGE)
