from datetime import timedelta
import logging

import pytest

from app.my_project.backend.presentation.url import ApiMainUrl, PageUrl
from app.my_project.backend.presentation.url import ALLOWED_REDIRECT_URLS
from core.constants.user import TokenName
from core.constants.error import (
    RedirectUrlNotAllowedError,
    NextMissingError,
    RefreshTokenMissingError,
)
from infrastructure.security.token import PyJWTSecurity
from dto.user import CreateUserDTO
from domain.exceptions import TokenExpired, InvalidToken
from test_data.constants import AppStorageTest, TEST_ALLOWED_REDIRECT_URLS


@pytest.mark.page
@pytest.mark.asyncio
async def test_valide_refresh_token_303(
    app_storage: AppStorageTest,
):
    username = "test name"
    password = "1234567890password"

    app_storage.app.state.jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(days=7),
    )

    create_user_response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )

    assert create_user_response.status_code == 200

    response_jwt = await app_storage.client.get(
        f"{PageUrl.USER_PAGE}",
        follow_redirects=False,
    )
    assert response_jwt.status_code == 303
    assert response_jwt.headers["location"] == f"{PageUrl.REFRESH_PAGE}?next=%2Fuser"


@pytest.mark.page
@pytest.mark.asyncio
async def test_valide_refresh_token_flow(
    app_storage: AppStorageTest,
):
    username = "test name"
    password = "1234567890password"

    create_user_response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )

    assert create_user_response.status_code == 200

    jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(days=7),
    )
    expired_access_token = jwt_security.create_access_token(user_id="1")

    app_storage.client.cookies.delete(name=TokenName.ACCESS_TOKEN.value)
    app_storage.client.cookies.set(
        name=TokenName.ACCESS_TOKEN.value,
        value=expired_access_token,
    )

    response_jwt = await app_storage.client.get(
        f"{PageUrl.USER_PAGE}",
        follow_redirects=True,
    )
    assert response_jwt.status_code == 200
    assert "<h2>My personal page</h2>" in response_jwt.text
    assert response_jwt.url.path == PageUrl.USER_PAGE


@pytest.mark.page
@pytest.mark.asyncio
async def test_expired_refresh_token(
    app_storage: AppStorageTest,
    caplog,
):
    username = "test name"
    password = "1234567890password"

    app_storage.app.state.jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(minutes=-1),
    )

    create_user_response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )

    assert create_user_response.status_code == 200
    with caplog.at_level(logging.WARNING):
        response_jwt = await app_storage.client.get(
            f"{PageUrl.USER_PAGE}",
            follow_redirects=True,
        )
        token_expired = TokenExpired()
        assert token_expired.error.message in caplog.text
        assert token_expired.error.code in caplog.text
        assert token_expired.status_code == response_jwt.status_code

    assert (
        response_jwt.cookies.get(
            TokenName.ACCESS_TOKEN.value,
            None,
        )
        is None
    )
    assert (
        response_jwt.cookies.get(
            TokenName.REFRESH_TOKEN.value,
            None,
        )
        is None
    )
    assert '<div class="session_expired-img">' in response_jwt.text
    assert response_jwt.url.path == PageUrl.REFRESH_PAGE


@pytest.mark.page
@pytest.mark.asyncio
async def test_invalide_refresh_token(app_storage: AppStorageTest, caplog):
    username = "test name123"
    password = "1234567890password123"

    app_storage.app.state.jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(days=7),
    )

    create_user_response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )

    assert create_user_response.status_code == 200

    app_storage.client.cookies.delete(name=TokenName.REFRESH_TOKEN.value)
    app_storage.client.cookies.set(
        name=TokenName.REFRESH_TOKEN.value,
        value="INVALID TOKEN",
    )
    with caplog.at_level(logging.WARNING):
        response_jwt = await app_storage.client.get(
            f"{PageUrl.USER_PAGE}",
            follow_redirects=True,
        )
        invalid_token = InvalidToken()
        assert invalid_token.error.message in caplog.text
        assert invalid_token.error.code in caplog.text
        assert invalid_token.status_code == response_jwt.status_code

    assert (
        response_jwt.cookies.get(
            TokenName.ACCESS_TOKEN.value,
            None,
        )
        is None
    )
    assert (
        response_jwt.cookies.get(
            TokenName.REFRESH_TOKEN.value,
            None,
        )
        is None
    )
    assert '<div class="session_expired-img">' in response_jwt.text
    assert response_jwt.url.path == PageUrl.REFRESH_PAGE


@pytest.mark.page
@pytest.mark.asyncio
async def test_not_allowed_redirect_urls(
    app_storage: AppStorageTest,
    caplog,
):
    username = "test name123"
    password = "1234567890password123"

    create_user_response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )

    assert create_user_response.status_code == 200

    app_storage.app.state.allowed_redirect_urls = TEST_ALLOWED_REDIRECT_URLS

    jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(days=7),
    )
    expired_access_token = jwt_security.create_access_token(user_id="1")

    app_storage.client.cookies.delete(name=TokenName.ACCESS_TOKEN.value)
    app_storage.client.cookies.set(
        name=TokenName.ACCESS_TOKEN.value,
        value=expired_access_token,
    )
    with caplog.at_level(logging.WARNING):
        response_jwt = await app_storage.client.get(
            f"{PageUrl.USER_PAGE}",
            follow_redirects=True,
        )
        message = RedirectUrlNotAllowedError.message % PageUrl.USER_PAGE
        assert message in caplog.text
        assert RedirectUrlNotAllowedError.code in caplog.text
        assert RedirectUrlNotAllowedError.status_code == response_jwt.status_code

    assert (
        response_jwt.cookies.get(
            TokenName.ACCESS_TOKEN.value,
            None,
        )
        is None
    )
    assert (
        response_jwt.cookies.get(
            TokenName.REFRESH_TOKEN.value,
            None,
        )
        is None
    )
    assert '<div class="forbidden-img">' in response_jwt.text
    assert response_jwt.url.path == PageUrl.REFRESH_PAGE


@pytest.mark.page
@pytest.mark.asyncio
async def test_allowed_redirect_urls(
    app_storage: AppStorageTest,
):
    username = "test name123"
    password = "1234567890password123"

    create_user_response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )

    assert create_user_response.status_code == 200

    jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(days=7),
    )
    expired_access_token = jwt_security.create_access_token(user_id="1")

    app_storage.app.state.allowed_redirect_urls = ALLOWED_REDIRECT_URLS

    app_storage.client.cookies.delete(name=TokenName.ACCESS_TOKEN.value)
    app_storage.client.cookies.set(
        name=TokenName.ACCESS_TOKEN.value,
        value=expired_access_token,
    )

    response_jwt = await app_storage.client.get(
        f"{PageUrl.USER_PAGE}",
        follow_redirects=True,
    )

    assert response_jwt.status_code == 200
    assert "<h2>My personal page</h2>" in response_jwt.text
    assert response_jwt.url.path == PageUrl.USER_PAGE


@pytest.mark.page
@pytest.mark.asyncio
async def test_refresh_without_next(
    app_storage: AppStorageTest,
    caplog,
):
    with caplog.at_level(logging.WARNING):
        response = await app_storage.client.get(
            f"{PageUrl.REFRESH_PAGE}",
            follow_redirects=False,
        )
        assert NextMissingError.message in caplog.text
        assert NextMissingError.code in caplog.text
        assert NextMissingError.status_code == response.status_code

    assert response.headers["location"] == PageUrl.MAIN_PAGE


@pytest.mark.page
@pytest.mark.asyncio
async def test_refresh_without_refresh_token(
    app_storage: AppStorageTest,
    caplog,
):
    with caplog.at_level(logging.WARNING):
        response = await app_storage.client.get(
            f"{PageUrl.REFRESH_PAGE}?next=%2Fuser",
            follow_redirects=False,
        )
        assert RefreshTokenMissingError.message in caplog.text
        assert RefreshTokenMissingError.code in caplog.text
        assert RefreshTokenMissingError.status_code == response.status_code

    assert response.headers["location"] == PageUrl.MAIN_PAGE


@pytest.mark.page
@pytest.mark.asyncio
async def test_refresh_without_refresh_token_flow(
    app_storage: AppStorageTest,
    caplog,
):
    username = "test name123"
    password = "1234567890password123"

    app_storage.app.state.jwt_security = PyJWTSecurity(
        access_token_lifetime=timedelta(minutes=-1),
        refresh_token_lifetime=timedelta(days=7),
    )

    create_user_response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )

    assert create_user_response.status_code == 200

    app_storage.client.cookies.delete(name=TokenName.REFRESH_TOKEN.value)
    with caplog.at_level(logging.WARNING):
        response_jwt = await app_storage.client.get(
            f"{PageUrl.USER_PAGE}",
            follow_redirects=True,
        )
        assert RefreshTokenMissingError.message in caplog.text
        assert RefreshTokenMissingError.code in caplog.text

    assert '<form id="login-form">' in response_jwt.text
    assert response_jwt.url.path == PageUrl.MAIN_PAGE
