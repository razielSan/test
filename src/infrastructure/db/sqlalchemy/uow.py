from typing import Optional, Type
from types import TracebackType
from typing_extensions import Self
from logging import Logger

from sqlalchemy.ext.asyncio import AsyncSession

from domain.db.base import UnitOfWorkProtocol, SessionFactoryProtocol
from infrastructure.db.sqlalchemy.repositories.user import SqlAlchemyUserRepository
from infrastructure.db.sqlalchemy.repositories.role import SqlAlchemyRoleRepository
from infrastructure.db.sqlalchemy.repositories.user_role import (
    SqlAlchemyUserRoleRepository,
)


class SQLAlchemyUnitOfWork(UnitOfWorkProtocol):
    def __init__(
        self,
        session_factory: SessionFactoryProtocol[AsyncSession],
        logger: Logger,
    ) -> None:
        self.session_factory: SessionFactoryProtocol[AsyncSession] = session_factory
        self.session: Optional[AsyncSession] = None
        self.logger = logger

    async def __aenter__(self) -> Self:
        self.session = await self.session_factory()
        self.user = SqlAlchemyUserRepository(
            session=self.session,
            logger=self.logger,
        )
        self.user_role = SqlAlchemyUserRoleRepository(
            session=self.session,
            logger=self.logger,
        )
        self.role = SqlAlchemyRoleRepository(
            session=self.session,
            logger=self.logger,
        )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self.session is None:
            return None

        try:
            if exc_val:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()
