import pytest

from app.my_project.backend.presentation.url import ApiMainUrl
from dto.user import UserDTO, CreateUserDTO, AuthenticateUserDTO
from test_data.db.redis import RateLimitTestProtocol
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_user(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    await test_rate_limit_service.clear()

    client = app_storage.client

    username = "test user"
    password = "123456789abca"

    created_user = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(
            username=username,
            password=password,
        ).model_dump(),
    )

    assert created_user.status_code == 200

    authed_user = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data=AuthenticateUserDTO(
            password=password,
            username=username,
        ).model_dump(),
    )

    assert authed_user.status_code == 204

    response = await client.get(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.GET_USER}",
    )
    assert response.status_code == 200
    user = UserDTO(**response.json())
    assert user.username == username

    await test_rate_limit_service.shutdown()
