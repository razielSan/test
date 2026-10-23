from datetime import timedelta

import pytest

from app.my_project.backend.presentation.url import ApiMainUrl, ApiAdminUrl
from core.constants.user import TokenName
from dto.exceptions import ErrorResponseDTO
from domain.exceptions import (
    InvalidToken,
    TokenExpired,
    UnauthorizedError,
)
from infrastructure.security.token import PyJWTSecurity
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_erorr_user_not_authorized(app_storage: AppStorageTest):
    response = await app_storage.client.get(
        f"{ApiAdminUrl.PREFIX}{ApiMainUrl.GET_USER}",
    )
    exception = UnauthorizedError()
    assert response.status_code == exception.status_code

    error = ErrorResponseDTO(**response.json())
    assert error.code == exception.error.code
    assert error.message == exception.error.message


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_user_invalid_token(app_storage: AppStorageTest):
    client = app_storage.client

    client.cookies.set(
        name=TokenName.ACCESS_TOKEN.value,
        value="INVALID TOKEN",
    )
    error_repsonse = await client.get(
        f"{ApiAdminUrl.PREFIX}{ApiMainUrl.GET_USER}",
    )
    exception = InvalidToken()
    assert error_repsonse.status_code == exception.status_code

    response = ErrorResponseDTO(**error_repsonse.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_user_expired_token(app_storage: AppStorageTest):
    client = app_storage.client

    token = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(days=7),
    ).create_access_token(user_id="10")
    client.cookies.set(
        name=TokenName.ACCESS_TOKEN.value,
        value=token,
    )
    error_repsonse = await client.get(
        f"{ApiAdminUrl.PREFIX}{ApiMainUrl.GET_USER}",
    )
    exception = TokenExpired()
    assert error_repsonse.status_code == exception.status_code

    response = ErrorResponseDTO(**error_repsonse.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message


@pytest.mark.api
@pytest.mark.asyncio
async def test_erorr_admin_not_authorized(app_storage: AppStorageTest):
    response = await app_storage.client.get(
        f"{ApiAdminUrl.PREFIX}{ApiAdminUrl.ADMIN_GET_USER}".format(user_id=1),
    )
    exception = UnauthorizedError()
    assert response.status_code == exception.status_code
    error = ErrorResponseDTO(**response.json())
    assert error.code == exception.error.code
    assert error.message == exception.error.message


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_admin_invalid_token(app_storage: AppStorageTest):
    client = app_storage.client

    client.cookies.set(
        name=TokenName.ACCESS_TOKEN.value,
        value="INVALID TOKEN",
    )
    error_repsonse = await client.get(
        f"{ApiAdminUrl.PREFIX}{ApiAdminUrl.ADMIN_GET_USER}".format(user_id=1),
    )
    exception = InvalidToken()
    assert error_repsonse.status_code == exception.status_code

    response = ErrorResponseDTO(**error_repsonse.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message
