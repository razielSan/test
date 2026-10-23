import pytest

from app.my_project.backend.presentation.url import ApiMainUrl
from app.my_project.backend.application.user.create_user import CreateUser
from domain.exceptions import UserAlreadyExists
from dto.user import (
    UpdateUserNameDTO,
    CreateUserDTO,
    AuthenticateUserDTO,
    UserDTO,
)
from dto.exceptions import ErrorResponseDTO
from infrastructure.security.hash import ArgonHasher
from test_data.db.redis import RateLimitTestProtocol
from test_data.constants import AppStorageTest


@pytest.mark.asyncio
@pytest.mark.api
async def test_update_username(
    app_storage: AppStorageTest,
):
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

    new_username = "test user2"
    updated_user = await client.patch(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.UPDATE_USERNAME}",
        json=UpdateUserNameDTO(
            password=password,
            username=new_username,
        ).model_dump(),
    )

    assert updated_user.status_code == 200
    user = UserDTO(**updated_user.json())

    response = await client.get(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.GET_USER}",
    )

    assert response.status_code == 200
    user_response = UserDTO(**response.json())

    assert user_response.username == user.username


@pytest.mark.asyncio
@pytest.mark.api
async def test_error_user_already_exists(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
    test_uow,
):
    await test_rate_limit_service.clear()

    client = app_storage.client

    username = "test user"
    password = "123456789abca"

    await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(
        CreateUserDTO(password=password, username=username),
    )
    username_2 = "test user2"

    await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(
        CreateUserDTO(password=password, username=username_2),
    )

    authed_user = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data=AuthenticateUserDTO(
            password=password,
            username=username,
        ).model_dump(),
    )

    assert authed_user.status_code == 204

    updated_user = await client.patch(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.UPDATE_USERNAME}",
        json=UpdateUserNameDTO(
            password=password,
            username=username_2,
        ).model_dump(),
    )
    exception = UserAlreadyExists()
    assert updated_user.status_code == exception.status_code

    response = ErrorResponseDTO(**updated_user.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message

    await test_rate_limit_service.shutdown()
