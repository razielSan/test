import pytest

from dto.user import CreateUserDTO, UpdateUserNameDTO
from domain.exceptions import UserNotFound, UserAlreadyExists
from app.my_project.backend.application.user.update_user import UpdateUserName
from app.my_project.backend.application.user.create_user import CreateUser
from app.my_project.backend.application.services.authentication import (
    AuthenticationService,
)
from infrastructure.security.hash import ArgonHasher


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_user_password_another_username(test_uow, logger):
    username = "test name"
    password = "12345678910abc"

    created_user = await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password=password, username=username),
    )

    new_username = "test_name1"
    updated_user = await UpdateUserName(
        uow=test_uow,
        auth_service=AuthenticationService(
            hasher=ArgonHasher(),
            logger=logger,
        ),
    ).execute(
        user=UpdateUserNameDTO(
            password=password,
            username=new_username,
        ),
        user_id=created_user.id,
    )
    assert updated_user.username == new_username


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_user_password_same_username(test_uow, logger):
    username = "test name"
    password = "12345678910abc"

    created_user = await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password=password, username=username),
    )

    updated_user = await UpdateUserName(
        uow=test_uow,
        auth_service=AuthenticationService(
            hasher=ArgonHasher(),
            logger=logger,
        ),
    ).execute(
        user=UpdateUserNameDTO(
            password=password,
            username=username,
        ),
        user_id=created_user.id,
    )
    assert updated_user.username == username


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_not_found(test_uow, logger):
    with pytest.raises(UserNotFound) as exc_info:
        await UpdateUserName(
            uow=test_uow,
            auth_service=AuthenticationService(
                hasher=ArgonHasher(),
                logger=logger,
            ),
        ).execute(
            user=UpdateUserNameDTO(password="12345678910abc", username="test name"),
            user_id=1,
        )
    assert exc_info.value.status_code == UserNotFound().status_code
    assert exc_info.value.error.code == UserNotFound().error.code
    assert exc_info.value.error.message == UserNotFound().error.message


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_already_exists(test_uow, logger):
    username1 = "test name"
    password = "12345678910abc"

    created_user_1 = await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password=password, username=username1),
    )

    username2 = "test name1"

    created_user_2 = await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password=password, username=username2),
    )

    with pytest.raises(UserAlreadyExists) as exc_info:
        await UpdateUserName(
            uow=test_uow,
            auth_service=AuthenticationService(
                hasher=ArgonHasher(),
                logger=logger,
            ),
        ).execute(
            user=UpdateUserNameDTO(
                password="12345678910abc",
                username=created_user_1.username,
            ),
            user_id=created_user_2.id,
        )
    assert exc_info.value.status_code == UserAlreadyExists().status_code
    assert exc_info.value.error.code == UserAlreadyExists().error.code
    assert exc_info.value.error.message == UserAlreadyExists().error.message
