import pytest

from app.my_project.backend.application.user.delete_user import DeleteUser
from app.my_project.backend.application.user.create_user import CreateUser
from dto.user import CreateUserDTO, UserDTO
from domain.exceptions import UserNotFound
from infrastructure.security.hash import ArgonHasher


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_one_user(test_uow):
    username = "test"
    password = "12345678910abc"
    user_create_dto = CreateUserDTO(
        password=password,
        username=username,
    )
    user_created = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(user=user_create_dto)

    assert user_created.username == user_create_dto.username

    deleted_user = await DeleteUser(
        uow=test_uow,
    ).execute(
        user=UserDTO(
            id=user_created.id,
            username=user_created.username,
            is_active=user_created.is_active,
        )
    )
    assert deleted_user.username == user_created.username

    user_created = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(user=user_create_dto)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password",
    [
        ("test1", "12345678910abc1"),
        ("test2", "12345678910abc2"),
        ("test3", "12345678910abc23"),
    ],
)
async def test_delete_many_users(
    test_uow,
    username,
    password,
):
    user_create_dto = CreateUserDTO(
        password=password,
        username=username,
    )
    user_created = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(user=user_create_dto)

    assert user_created.username == user_create_dto.username

    deleted_user = await DeleteUser(
        uow=test_uow,
    ).execute(
        user=UserDTO(
            id=user_created.id,
            username=user_created.username,
            is_active=user_created.is_active,
        )
    )
    assert deleted_user.username == user_created.username

    user_created = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(user=user_create_dto)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_user_not_found(test_uow):
    user_id = 10
    username = "test"
    is_active = True
    with pytest.raises(UserNotFound) as exc_info:
        await DeleteUser(
            uow=test_uow,
        ).execute(
            user=UserDTO(
                id=user_id,
                username=username,
                is_active=is_active,
            )
        )

    assert exc_info.value.error.code == UserNotFound().error.code
    assert exc_info.value.error.message == UserNotFound().error.message
    assert exc_info.value.status_code == UserNotFound().status_code
