from typing import Sequence
from logging import Logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from domain.db.repositories.role import AbstractRoleRepository
from domain.db.models.role import RoleDOMAIN
from domain.exceptions import NameDoesNotExists
from infrastructure.db.sqlalchemy.models.user_role import Role


class SqlAlchemyRoleRepository(AbstractRoleRepository):
    MODEL = Role

    def __init__(self, session: AsyncSession, logger: Logger) -> None:
        self.session = session
        self.logger = logger

    async def create_roles(self, roles: Sequence[str]) -> None:
        try:
            query = select(self.MODEL.name).where(self.MODEL.name.in_(roles))
            result = await self.session.scalars(query)
            exsisting_roles = set(result)
            for role_name in set(roles) - exsisting_roles:
                self.session.add(self.MODEL(name=role_name))
        except OperationalError as err:
            self.logger.error(str(err))
            raise

    async def get_by_name(self, name: str) -> RoleDOMAIN:
        query = select(self.MODEL).where(self.MODEL.name == name)
        result = await self.session.execute(query)
        role = result.scalar()
        if role is None:
            raise NameDoesNotExists(name=name)

        return RoleDOMAIN(id=role.id, name=role.name)

    async def all_roles_exists(self, roles: Sequence[str]) -> bool:
        results = await self.session.scalars(
            select(self.MODEL.name).where(
                self.MODEL.name.in_(roles),
            )
        )
        names = set(results)
        return names == set(roles)
