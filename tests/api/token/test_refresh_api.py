import asyncio
from datetime import timedelta

import pytest
from httpx import Response

from app.my_project.backend.presentation.url import ApiMainUrl
from app.my_project.backend.application.user.create_user import CreateUser
from core.constants.user import TokenName
from dto.user import CreateUserDTO
from domain.exceptions import TokenExpired, ErrorResponse, InvalidToken
from test_data.db.redis import RateLimitTestProtocol
from infrastructure.security.token import PyJWTSecurity
from infrastructure.security.hash import ArgonHasher
from core.constants.user import ResponseMessageUser
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_new_access_token(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
    test_uow,
):
    await test_rate_limit_service.clear()

    client = app_storage.client

    username = "test"
    password = "123456789abca"

    await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(
        CreateUserDTO(password=password, username=username),
    )
    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": username,
            "password": password,
        },
    )
    auth_token_access = response_authenticate.cookies.get(TokenName.ACCESS_TOKEN.value)
    assert isinstance(auth_token_access, str)
    assert response_authenticate.status_code == 204

    await asyncio.sleep(1)
    response: Response = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REFRESH}",
    )
    update_acces_token = response.cookies.get(TokenName.ACCESS_TOKEN.value)
    assert auth_token_access != update_acces_token

    assert response.status_code == 200
    token = response.json()
    assert token == ResponseMessageUser.UPDATE_ACCESS_TOKEN_SUCCESS

    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_valid_refresh_token(app_storage: AppStorageTest):
    client = app_storage.client

    token = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=15),
        refresh_token_lifetime=timedelta(days=7),
    ).create_refresh_token(user_id="10")

    client.cookies.set(name=TokenName.REFRESH_TOKEN.value, value=token)
    response = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REFRESH}",
    )

    assert response.status_code == 200
    token = response.json()
    assert token == ResponseMessageUser.UPDATE_ACCESS_TOKEN_SUCCESS


@pytest.mark.api
@pytest.mark.asyncio
async def test_expired_refresh_token(app_storage: AppStorageTest):
    client = app_storage.client

    token = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=15),
        refresh_token_lifetime=timedelta(minutes=0),
    ).create_refresh_token(user_id="10")
    client.cookies.set(name=TokenName.REFRESH_TOKEN.value, value=token)
    response = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REFRESH}",
    )
    exception = TokenExpired()
    assert response.status_code == exception.status_code
    result = ErrorResponse(**response.json())
    assert result.message == exception.error.message
    assert result.code == exception.error.code


@pytest.mark.api
@pytest.mark.asyncio
async def test_invalid_refresh_token(app_storage: AppStorageTest):
    client = app_storage.client

    client.cookies.set(name=TokenName.REFRESH_TOKEN.value, value="INVALID TOKEN")
    response = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REFRESH}",
    )
    exception = InvalidToken()
    assert response.status_code == exception.status_code
    result = ErrorResponse(**response.json())
    assert result.message == exception.error.message
    assert result.code == exception.error.code
