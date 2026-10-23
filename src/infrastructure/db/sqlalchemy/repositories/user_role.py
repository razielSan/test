from logging import Logger
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.db.repositories.user_role import AbstractUserRoleRepository
from domain.db.models.role import RoleDOMAIN
from domain.db.models.user import UserDOMAIN
from infrastructure.db.sqlalchemy.models.user_role import User, Role, UserRole


class SqlAlchemyUserRoleRepository(AbstractUserRoleRepository):
    MODEL = UserRole

    def __init__(self, session: AsyncSession, logger: Logger) -> None:
        self.session = session
        self.logger = logger

    async def add(self, user_id: int, role_id: int) -> None:
        user_role = self.MODEL(user_id=user_id, role_id=role_id)
        self.session.add(user_role)

    async def get_roles(self, user_id: int) -> List[RoleDOMAIN]:
        query = (
            select(Role)
            .join(self.MODEL, Role.id == self.MODEL.role_id)
            .where(self.MODEL.user_id == user_id)
        )
        result = await self.session.execute(query)
        roles = result.scalars().all()
        return [RoleDOMAIN(id=role.id, name=role.name) for role in roles]

    async def get_users(self, role_id: int) -> List[UserDOMAIN]:
        query = (
            select(User)
            .join(
                self.MODEL,
                User.id == self.MODEL.user_id,
            )
            .where(self.MODEL.role_id == role_id)
        )
        result = await self.session.execute(query)
        users = result.scalars().all()
        return [
            UserDOMAIN(
                id=user.id,
                username=user.username,
                password_hash=user.password_hash,
                is_active=user.is_active,
            )
            for user in users
        ]
