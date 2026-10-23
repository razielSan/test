import pytest
import logging
from datetime import timedelta

from app.my_project.backend.presentation.url import ApiMainUrl
from domain.exceptions import TokenExpired, InvalidToken
from core.constants.user import ResponseMessageUser
from core.constants.error import RefreshTokenMissingError
from core.constants.user import TokenName
from dto.exceptions import ErrorResponseDTO
from dto.user import CreateUserDTO
from infrastructure.security.token import PyJWTSecurity
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_access_token_success(
    app_storage: AppStorageTest,
):
    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password="12345678asdffgghhh", username="test").model_dump(),
    )

    assert response.status_code == 200

    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REFRESH}",
    )

    assert response.status_code == 200
    assert response.json() == ResponseMessageUser.UPDATE_ACCESS_TOKEN_SUCCESS


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_access_token_missing_refersh(
    app_storage: AppStorageTest,
    caplog,
):
    with caplog.at_level(logging.WARNING):
        response = await app_storage.client.post(
            f"{ApiMainUrl.PREFIX}{ApiMainUrl.REFRESH}",
        )
        assert RefreshTokenMissingError.code in caplog.text
        assert RefreshTokenMissingError.message in caplog.text

    assert response.json() == ResponseMessageUser.NOT_AUTHTENTICATE


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_access_token_token_invalid(
    app_storage: AppStorageTest,
):
    app_storage.client.cookies.set(
        name=TokenName.REFRESH_TOKEN.value,
        value="INVALID TOKEN",
    )
    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REFRESH}",
    )
    exception = InvalidToken()

    assert response.status_code == exception.status_code

    error_response = ErrorResponseDTO(**response.json())
    assert exception.error.code == error_response.code
    assert exception.error.message == error_response.message


@pytest.mark.api
@pytest.mark.asyncio
async def test_update_access_token_token_expired(
    app_storage: AppStorageTest,
):
    app_storage.app.state.jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(days=-1),
    )

    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password="12345678asdffgghhh", username="test").model_dump(),
    )

    assert response.status_code == 200

    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REFRESH}",
    )
    exception = TokenExpired()

    assert response.status_code == exception.status_code

    error_response = ErrorResponseDTO(**response.json())
    assert exception.error.message == error_response.message
    assert exception.error.code == error_response.code
