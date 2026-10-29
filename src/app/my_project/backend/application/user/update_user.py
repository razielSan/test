from app.my_project.backend.application.services.authentication import (
    AuthenticationServiceProtocol,
)
from dto.user import UpdateUserPasswordDTO, UserDTO, UpdateUserNameDTO
from domain.db.base import UnitOfWorkProtocol


class UpdateUserPassword:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        auth_service: AuthenticationServiceProtocol,
    ) -> None:
        self.uow = uow
        self.auth_service = auth_service

    async def execute(
        self,
        user: UpdateUserPasswordDTO,
        user_id: int,
    ) -> UserDTO:
        async with self.uow as uow:
            user_authed = await self.auth_service.verify_user_password(
                uow=uow,
                user_id=user_id,
                password=user.password,
            )
            new_password_hash = self.auth_service.calculate_new_hash(
                password=user.new_password,
            )

            updated_user = await uow.user.update_password(
                user_id=user_authed.id,
                password_hash=new_password_hash,
            )

        return UserDTO(
            id=updated_user.id,
            username=updated_user.username,
            is_active=updated_user.is_active,
        )


class UpdateUserName:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        auth_service: AuthenticationServiceProtocol,
    ) -> None:
        self.uow = uow
        self.auth_service = auth_service

    async def execute(
        self,
        user: UpdateUserNameDTO,
        user_id: int,
    ) -> UserDTO:
        async with self.uow as uow:
            user_authed = await self.auth_service.verify_user_password(
                uow=uow,
                user_id=user_id,
                password=user.password,
            )

            updated_user = await uow.user.update_username(
                user_id=user_authed.id,
                username=user.username,
            )

        return UserDTO(
            id=updated_user.id,
            username=updated_user.username,
            is_active=updated_user.is_active,
        )
