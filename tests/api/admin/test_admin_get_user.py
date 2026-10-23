import pytest

from app.my_project.backend.application.user.create_user import CreateUser
from app.my_project.backend.presentation.url import ApiMainUrl, ApiAdminUrl
from dto.user import CreateUserDTO, UserDTO
from dto.exceptions import ErrorResponseDTO
from domain.db.constants import Role
from domain.exceptions import AdminAccessRequired
from test_data.db.redis import RateLimitTestProtocol
from infrastructure.security.hash import ArgonHasher
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_admin(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
    test_uow,
) -> None:
    await test_rate_limit_service.clear()

    client = app_storage.client
    username = "admin"
    password = "123456789abca"
    admin = await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password=password, username=username),
        role_name=Role.admin.value,
    )

    authed_admin = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={"username": username, "password": password},
    )
    assert authed_admin.status_code == 204

    received_admin = await client.get(
        f"{ApiAdminUrl.PREFIX}{ApiAdminUrl.ADMIN_GET_USER}".format(
            user_id=admin.id,
        ),
    )

    assert received_admin.status_code == 200

    response = UserDTO(**received_admin.json())
    assert response.id == admin.id
    assert response.username == admin.username

    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_admin_getting_information_about_users(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
    test_uow,
) -> None:
    await test_rate_limit_service.clear()

    client = app_storage.client
    username = "admin"
    password = "123456789abca"

    await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password=password, username=username),
        role_name=Role.admin.value,
    )

    user_1 = await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password="1211111dsdsdsds111", username="user 1"),
    )

    user_2 = await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password="1211111dsdsdsds111", username="user 2"),
    )

    authed_admin = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={"username": username, "password": password},
    )
    assert authed_admin.status_code == 204

    received_admin_get_user_1 = await client.get(
        f"{ApiAdminUrl.PREFIX}{ApiAdminUrl.ADMIN_GET_USER}".format(
            user_id=user_1.id,
        ),
    )

    assert received_admin_get_user_1.status_code == 200

    user_1_received = UserDTO(**received_admin_get_user_1.json())
    assert user_1_received.id == user_1.id
    assert user_1_received.username == user_1.username

    received_admin_get_user_2 = await client.get(
        f"{ApiAdminUrl.PREFIX}{ApiAdminUrl.ADMIN_GET_USER}".format(
            user_id=user_2.id,
        ),
    )

    assert received_admin_get_user_2.status_code == 200

    user_2_received = UserDTO(**received_admin_get_user_2.json())
    assert user_2_received.id == user_2.id
    assert user_2_received.username == user_2.username
    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_admin_access_required(
    app_storage: AppStorageTest,
) -> None:
    client = app_storage.client
    username = "test"
    password = "123456789abca"
    response_register = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )

    assert response_register.status_code == 200

    user = UserDTO(**response_register.json())

    admin_response = await client.get(
        f"{ApiAdminUrl.PREFIX}{ApiAdminUrl.ADMIN_GET_USER.format(user_id=user.id)}",
    )

    exception = AdminAccessRequired()
    assert admin_response.status_code == exception.status_code

    response = ErrorResponseDTO(**admin_response.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message
