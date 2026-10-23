import pytest

from dto.user import CreateUserDTO, UpdateUserPasswordDTO, AuthenticateUserDTO
from domain.exceptions import UserNotFound
from app.my_project.backend.application.user.update_user import UpdateUserPassword
from app.my_project.backend.application.user.authenticate_user import AuthenticateUser
from app.my_project.backend.application.user.create_user import CreateUser
from app.my_project.backend.application.services.authentication import (
    AuthenticationService,
)
from infrastructure.security.hash import ArgonHasher


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_user_password_another_password(test_uow, logger):
    username = "test name"
    password = "12345678910abc"

    created_user = await CreateUser(uow=test_uow, hasher=ArgonHasher()).execute(
        user=CreateUserDTO(password=password, username=username),
    )

    new_password = "12345678910abc1"
    updated_user = await UpdateUserPassword(
        uow=test_uow,
        auth_service=AuthenticationService(
            hasher=ArgonHasher(),
            logger=logger,
        ),
    ).execute(
        user=UpdateUserPasswordDTO(
            password=password,
            new_password=new_password,
        ),
        user_id=created_user.id,
    )

    user = await AuthenticateUser(
        uow=test_uow,
        auth_service=AuthenticationService(
            hasher=ArgonHasher(),
            logger=logger,
        ),
    ).execute(
        user=AuthenticateUserDTO(
            password=new_password,
            username=username,
        )
    )

    assert user.id == updated_user.id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_user_password_same_password(test_uow, logger):
    username = "test name"
    password = "12345678910abc"

    created_user = await CreateUser(
        uow=test_uow,
        hasher=ArgonHasher(),
    ).execute(
        user=CreateUserDTO(
            password=password,
            username=username,
        ),
    )

    updated_user = await UpdateUserPassword(
        uow=test_uow,
        auth_service=AuthenticationService(
            hasher=ArgonHasher(),
            logger=logger,
        ),
    ).execute(
        user=UpdateUserPasswordDTO(
            password=password,
            new_password=password,
        ),
        user_id=created_user.id,
    )

    user = await AuthenticateUser(
        uow=test_uow,
        auth_service=AuthenticationService(
            hasher=ArgonHasher(),
            logger=logger,
        ),
    ).execute(
        user=AuthenticateUserDTO(
            password=password,
            username=username,
        ),
    )

    assert user.id == updated_user.id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_not_found(test_uow, logger):
    with pytest.raises(UserNotFound) as exc_info:
        await UpdateUserPassword(
            uow=test_uow,
            auth_service=AuthenticationService(
                hasher=ArgonHasher(),
                logger=logger,
            ),
        ).execute(
            user=UpdateUserPasswordDTO(
                password="12345678910abc1",
                new_password="12345678910abc2",
            ),
            user_id=1,
        )
    assert exc_info.value.status_code == UserNotFound().status_code
    assert exc_info.value.error.code == UserNotFound().error.code
    assert exc_info.value.error.message == UserNotFound().error.message
