from typing import Protocol, Optional
from logging import Logger

from core.log.message import UserLog
from dto.user import AuthenticateUserDTO, UserDTO
from domain.exceptions import UserNotFound
from domain.db.models.user import UserDOMAIN
from domain.db.base import UnitOfWorkProtocol
from domain.security.hasher import PasswordHasherProtocol


class AuthenticationServiceProtocol(Protocol):
    async def authenticate(
        self,
        uow: UnitOfWorkProtocol,
        user: AuthenticateUserDTO,
    ) -> UserDTO:
        pass

    def calculate_new_hash(self, password: str) -> str:
        pass

    async def verify_user_password(
        self,
        uow: UnitOfWorkProtocol,
        user_id: int,
        password: str,
    ) -> UserDTO:
        pass


class AuthenticationService:
    def __init__(self, hasher: PasswordHasherProtocol, logger: Logger) -> None:
        self.hasher = hasher
        self.logger = logger

    async def authenticate(
        self,
        uow: UnitOfWorkProtocol,
        user: AuthenticateUserDTO,
    ) -> UserDTO:
        user_success: Optional[UserDOMAIN] = await uow.user.get_user(
            username=user.username,
        )

        if user_success is None:
            raise UserNotFound(username=user.username)

        self.hasher.verify(
            password_hash=user_success.password_hash,
            password=user.password,
        )

        self.logger.info(UserLog.AUTHENTICATED.value, user.username)
        return UserDTO(
            id=user_success.id,
            username=user_success.username,
            is_active=user_success.is_active,
        )

    async def verify_user_password(
        self,
        uow: UnitOfWorkProtocol,
        user_id: int,
        password: str,
    ) -> UserDTO:
        user_success: Optional[UserDOMAIN] = await uow.user.get_user_by_id(
            user_id=user_id,
        )
        if user_success is None:
            raise UserNotFound(user_id=user_id)
        self.hasher.verify(
            password_hash=user_success.password_hash,
            password=password,
        )

        self.logger.info(UserLog.AUTHENTICATED.value, user_success.username)
        return UserDTO(
            id=user_success.id,
            username=user_success.username,
            is_active=user_success.is_active,
        )

    def calculate_new_hash(self, password: str) -> str:
        return self.hasher.hash(password=password)
