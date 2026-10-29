from typing import Optional, Protocol, Literal

from fastapi import Response

from core.constants.user import TokenName


Status_Somesite = Literal["lax", "strict", "none"]


class CookieApiProtocol(Protocol):
    def set_auth_cookies(
        self,
        response: Response,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        pass

    def delete_cookie(
        self,
        token_name: str,
        response: Response,
    ) -> None:
        pass


class CookieApi:
    def __init__(
        self,
        httponly: bool,
        samesite: Status_Somesite,
        secure: bool,
        path: str,
    ) -> None:
        self.httponly: bool = httponly
        self.samesite: Status_Somesite = samesite
        self.secure: bool = secure
        self.path: str = path

    def set_auth_cookies(
        self,
        response: Response,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        if access_token is not None:
            response.set_cookie(
                key=TokenName.ACCESS_TOKEN.value,
                value=access_token,
                httponly=self.httponly,
                samesite=self.samesite,
                secure=self.secure,
                path=self.path,
            )
        if refresh_token is not None:
            response.set_cookie(
                key=TokenName.REFRESH_TOKEN.value,
                value=refresh_token,
                httponly=self.httponly,
                samesite=self.samesite,
                secure=self.secure,
                path=self.path,
            )

    def delete_cookie(
        self,
        token_name: str,
        response: Response,
    ) -> None:
        response.delete_cookie(
            key=token_name,
            httponly=self.httponly,
            secure=self.secure,
            samesite=self.samesite,
            path=self.path,
        )
