import pytest

from app.my_project.backend.presentation.url import ApiMainUrl
from app.my_project.backend.application.user.create_user import CreateUser
from dto.user import CreateUserDTO
from dto.exceptions import ErrorResponseDTO
from domain.exceptions import AuthenticatedError
from infrastructure.security.hash import ArgonHasher
from test_data.db.redis import RateLimitTestProtocol
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_authenticate_user(
    app_storage: AppStorageTest, test_rate_limit_service: RateLimitTestProtocol, test_uow
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

    assert response_authenticate.status_code == 204

    response = await client.get(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.GET_USER}",
    )

    assert response.status_code == 200
    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_user_not_created(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    await test_rate_limit_service.clear()

    username = "test"
    password = "123456789abca"

    response_authenticate = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": username,
            "password": password,
        },
    )

    exception = AuthenticatedError()
    assert response_authenticate.status_code == exception.status_code

    response = ErrorResponseDTO(**response_authenticate.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message

    await test_rate_limit_service.shutdown()
