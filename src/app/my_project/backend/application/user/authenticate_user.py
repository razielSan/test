from app.my_project.backend.application.services.authentication import (
    AuthenticationServiceProtocol,
)
from dto.user import UserDTO, AuthenticateUserDTO
from domain.exceptions import UserNotFound, IncorrectPassword, AuthenticatedError
from domain.db.base import UnitOfWorkProtocol


class AuthenticateUser:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        auth_service: AuthenticationServiceProtocol,
    ) -> None:
        self.uow = uow
        self.auth_service = auth_service

    async def execute(self, user: AuthenticateUserDTO) -> UserDTO:
        try:
            async with self.uow as uow:
                authenticated_user = await self.auth_service.authenticate(
                    uow=uow,
                    user=user,
                )
        except (UserNotFound, IncorrectPassword) as err:
            raise AuthenticatedError() from err
        return UserDTO(
            id=authenticated_user.id,
            username=authenticated_user.username,
            is_active=authenticated_user.is_active,
        )
