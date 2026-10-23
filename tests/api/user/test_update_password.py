import pytest

from app.my_project.backend.presentation.url import ApiMainUrl
from dto.user import (
    UpdateUserPasswordDTO,
    CreateUserDTO,
    AuthenticateUserDTO,
    UserDTO,
)
from dto.exceptions import ErrorResponseDTO
from domain.exceptions import IncorrectPassword
from test_data.db.redis import RateLimitTestProtocol
from test_data.constants import AppStorageTest


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_password(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    await test_rate_limit_service.clear()

    client = app_storage.client

    username = "test user"
    password = "12345678910abc"

    created_user = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(
            password=password,
            username=username,
        ).model_dump(),
    )

    assert created_user.status_code == 200

    new_password = "123456789abca"
    updated_user = await client.patch(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.UPDATE_USER_PASSWORD}",
        json=UpdateUserPasswordDTO(
            password=password,
            new_password=new_password,
        ).model_dump(),
    )

    assert updated_user.status_code == 200
    user = UserDTO(**updated_user.json())

    response = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data=AuthenticateUserDTO(
            password=new_password,
            username=user.username,
        ).model_dump(),
    )

    assert response.status_code == 204

    await test_rate_limit_service.shutdown()


@pytest.mark.asyncio
@pytest.mark.api
async def test_incorrect_password(
    app_storage: AppStorageTest,
):
    client = app_storage.client

    username = "test user"
    password = "123456789abca"

    created_user = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(
            password=password,
            username=username,
        ).model_dump(),
    )

    assert created_user.status_code == 200

    wrong_password = "123456789abcaasdsad"
    new_password = "1234567910abc"
    updated_user = await client.patch(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.UPDATE_USER_PASSWORD}",
        json=UpdateUserPasswordDTO(
            password=wrong_password,
            new_password=new_password,
        ).model_dump(),
    )

    exception = IncorrectPassword()
    assert updated_user.status_code == exception.status_code

    response = ErrorResponseDTO(**updated_user.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message
