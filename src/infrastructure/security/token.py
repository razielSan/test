from typing import Dict, Any, Protocol
from datetime import datetime, timedelta

import jwt
from fastapi import Response

from app.my_project.backend.application.api.cookies import CookieApiProtocol
from domain.exceptions import InvalidToken, TokenExpired
from core.constants.user import TokenType
from core.constants.error import DefaultError
from dto.user import TokenDTO
from settings.config import settings


class JWTSecurityProtocol(Protocol):
    def create_access_token(
        self,
        user_id: str,
    ) -> str:
        pass

    def decode_access_token(self, token: str) -> TokenDTO:
        pass

    def create_refresh_token(
        self,
        user_id: str,
    ) -> str:
        pass

    def decode_refresh_token(self, token: str) -> TokenDTO:
        pass


class PyJWTSecurity:
    def __init__(
        self,
        access_token_lifetime: timedelta,
        refresh_token_lifetime: timedelta,
    ) -> None:
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime

    def create_access_token(
        self,
        user_id: str,
    ) -> str:
        return self._create_token(
            user_id=user_id,
            type_token=TokenType.ACCESS.value,
            secret_key=settings.SECRET_KEY_TOKEN,
            time_delta=self.access_token_lifetime,
        )

    def decode_access_token(self, token: str) -> TokenDTO:
        payload = self._decode_token(
            token=token,
            secret_key=settings.SECRET_KEY_TOKEN,
        )
        if payload.type_token != TokenType.ACCESS.value:
            raise InvalidToken()
        return payload

    def create_refresh_token(
        self,
        user_id: str,
    ) -> str:
        return self._create_token(
            user_id=user_id,
            type_token=TokenType.REFRESH.value,
            secret_key=settings.SECRET_KEY_TOKEN_REFRESH,
            time_delta=self.refresh_token_lifetime,
        )

    def decode_refresh_token(self, token: str) -> TokenDTO:
        payload = self._decode_token(
            token=token,
            secret_key=settings.SECRET_KEY_TOKEN_REFRESH,
        )
        if payload.type_token != TokenType.REFRESH.value:
            raise InvalidToken()
        return payload

    @staticmethod
    def _create_token(
        user_id: str,
        type_token: str,
        secret_key: str,
        time_delta: timedelta,
    ) -> str:
        expire = datetime.utcnow() + time_delta
        token = TokenDTO(
            sub=user_id,
            exp=expire,
            type_token=type_token,
        )
        return jwt.encode(
            token.model_dump(),
            secret_key,
            settings.ALGORITHM_TOKEN,
        )

    @staticmethod
    def _decode_token(
        token: str,
        secret_key: str,
    ) -> TokenDTO:
        try:
            jwt_token: Dict[str, Any] = jwt.decode(
                token,
                secret_key,
                algorithms=[settings.ALGORITHM_TOKEN],
            )
            return TokenDTO(**jwt_token)
        except jwt.ExpiredSignatureError as err:
            raise TokenExpired() from err
        except jwt.PyJWTError as err:
            raise InvalidToken() from err
        except Exception as err:
            raise ValueError(DefaultError.message) from err


def set_auth_user_by_tokens_and_cookies(
    cookie_api: CookieApiProtocol,
    user_id: str,
    response: Response,
    jwt_security: JWTSecurityProtocol,
) -> None:
    access_token = jwt_security.create_access_token(
        user_id=user_id,
    )
    refresh_token = jwt_security.create_refresh_token(
        user_id=user_id,
    )

    cookie_api.set_auth_cookies(
        response=response,
        refresh_token=refresh_token,
        access_token=access_token,
    )
