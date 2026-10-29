from typing import Optional
from logging import Logger

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from core.log.message import UserLog
from infrastructure.db.sqlalchemy.models.user_role import User
from domain.db.repositories.user import AbsctractUserRepository
from domain.exceptions import UserAlreadyExists, UserNotFound
from domain.db.models.user import UserDOMAIN


class SqlAlchemyUserRepository(AbsctractUserRepository):
    MODEL = User

    def __init__(self, session: AsyncSession, logger: Logger) -> None:
        self.session = session
        self.logger = logger

    async def create_user(
        self,
        username: str,
        password_hash: str,
    ) -> UserDOMAIN:
        try:
            user: User = self.MODEL(username=username, password_hash=password_hash, is_active=True)
            self.session.add(user)
            await self.session.flush()

            self.logger.info(UserLog.CREATED.value, username)
            return UserDOMAIN(
                id=user.id,
                username=user.username,
                password_hash=user.password_hash,
                is_active=True,
            )
        except IntegrityError as err:
            raise UserAlreadyExists(username=username) from err

    async def delete_user(self, user_id: int) -> int:
        query = (
            delete(self.MODEL)
            .where(
                self.MODEL.id == user_id,
            )
            .returning(self.MODEL.id)
        )

        result_deleted = await self.session.execute(query)
        id_user = result_deleted.scalar()
        if id_user is None:
            raise UserNotFound(user_id=user_id)
        self.logger.info(UserLog.DELETED.value, id_user)
        return id_user

    async def get_user(self, username: str) -> Optional[UserDOMAIN]:
        query = select(self.MODEL).where(self.MODEL.username == username)
        user = await self.session.scalar(query)
        if not user:
            return None

        return UserDOMAIN(
            id=user.id,
            username=user.username,
            password_hash=user.password_hash,
            is_active=user.is_active,
        )

    async def get_user_by_id(self, user_id: int) -> Optional[UserDOMAIN]:
        query = select(self.MODEL).where(self.MODEL.id == user_id)
        user = await self.session.scalar(query)
        if not user:
            return None

        return UserDOMAIN(
            id=user.id,
            username=user.username,
            password_hash=user.password_hash,
            is_active=user.is_active,
        )

    async def update_username(
        self,
        user_id: int,
        username: str,
    ) -> UserDOMAIN:
        query = (
            update(self.MODEL)
            .where(self.MODEL.id == user_id)
            .values(
                username=username,
            )
            .returning(self.MODEL)
        )
        try:
            result_updated = await self.session.execute(query)
            user = result_updated.scalar_one_or_none()
        except IntegrityError as err:
            raise UserAlreadyExists(username=username) from err

        if user is None:
            raise UserNotFound(username=username)

        self.logger.info(UserLog.UPDATED.value, username)
        return UserDOMAIN(
            id=user.id,
            username=user.username,
            password_hash=user.password_hash,
            is_active=user.is_active,
        )

    async def update_password(
        self,
        user_id: int,
        password_hash: str,
    ) -> UserDOMAIN:
        query = (
            update(self.MODEL)
            .where(self.MODEL.id == user_id)
            .values(
                password_hash=password_hash,
            )
            .returning(self.MODEL)
        )
        result_updated = await self.session.execute(query)
        user = result_updated.scalar_one_or_none()

        if user is None:
            raise UserNotFound(user_id=user_id)

        self.logger.info(UserLog.UPDATED.value, user.username)
        return UserDOMAIN(
            id=user.id,
            username=user.username,
            password_hash=user.password_hash,
            is_active=user.is_active,
        )
