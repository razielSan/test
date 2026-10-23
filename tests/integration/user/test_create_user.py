import pytest

from app.my_project.backend.application.user.create_user import CreateUser
from domain.exceptions import UserAlreadyExists
from domain.db.base import UnitOfWorkProtocol
from domain.db.constants import Role
from dto.user import CreateUserDTO
from infrastructure.security.hash import ArgonHasher


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_admin(test_uow):
    password = "12345678910abc"
    username = "test admin"
    created_user = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(
        CreateUserDTO(
            password=password,
            username=username,
        ),
        role_name=Role.admin.value,
    )
    async with test_uow as uow:
        user_role = await uow.user_role.get_roles(
            user_id=created_user.id,
        )
    role = user_role[0]
    assert len(user_role) == 1
    assert role.name == Role.admin.value
    assert created_user.username == username


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_one_user(test_uow):
    password = "12345678910abc"
    username = "test username"
    created_user = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(CreateUserDTO(password=password, username=username))
    async with test_uow as uow:
        user_roles = await uow.user_role.get_roles(
            user_id=created_user.id,
        )
    role = user_roles[0]
    assert len(user_roles) == 1
    assert role.name == Role.user.value
    assert created_user.username == username


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password",
    [
        ("test_username1", "12345678910abc"),
        ("test_username2", "12345678910abc1"),
        ("test_username3", "12345678910abc2"),
        ("test_username4", "12345678910abc3"),
        ("test_username5", "12345678910abc5"),
    ],
)
async def test_create_many_users(
    test_uow: UnitOfWorkProtocol,
    username: str,
    password: str,
):
    created_user = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(CreateUserDTO(password=password, username=username))

    async with test_uow as uow:
        user_roles = await uow.user_role.get_roles(
            user_id=created_user.id,
        )
    role = user_roles[0]
    assert len(user_roles) == 1
    assert role.name == Role.user.value
    assert created_user.username == username


@pytest.mark.integration
@pytest.mark.asyncio
async def test_exception_user_already_exists(test_uow):
    password = "12345678910abc"
    username = "test username"
    created_user = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(CreateUserDTO(password=password, username=username))
    assert created_user.username == username

    new_password = "12345678910abc1"

    with pytest.raises(UserAlreadyExists) as exc_info:
        await CreateUser(
            uow=test_uow,
            hasher=ArgonHasher(),
        ).execute(CreateUserDTO(password=new_password, username=username))
    assert exc_info.value.error.code == UserAlreadyExists().error.code
    assert exc_info.value.error.message == UserAlreadyExists().error.message
    assert exc_info.value.status_code == UserAlreadyExists().status_code
