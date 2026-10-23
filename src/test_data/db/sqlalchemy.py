import logging
from pathlib import Path

from sqlalchemy import delete

from domain.db.base import AbstractBackend
from domain.db.constants import roles
from infrastructure.db.sqlalchemy.uow import SQLAlchemyUnitOfWork
from infrastructure.db.sqlalchemy.session import SessionFactorySQLAlchemy
from infrastructure.db.sqlalchemy.models import Base
from test_data.paths import test_database_url


def drop_table(table_path: Path) -> None:
    if table_path.is_file():
        table_path.unlink()


class DatabaseDelete:
    def __init__(
        self,
        session_factory: SessionFactorySQLAlchemy,
    ) -> None:
        self._session_factory = session_factory

    async def delete_database(self) -> None:
        await self._session_factory.engine.dispose()
        drop_table(table_path=test_database_url.delete_test_sqlite_path)


class SQLAlchemyBackend(AbstractBackend):
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
        self._session_factory = SessionFactorySQLAlchemy(
            database=self.database_url,
        )

    async def create_tables(self) -> None:
        async with self._session_factory.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_defaults_roles(self) -> None:
        async with self.get_uow() as uow:
            await uow.role.create_roles(roles=roles)

    def get_uow(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(
            session_factory=self._session_factory,
            logger=self.logger,
        )

    async def cleare_database(self) -> None:
        session = await self._session_factory()

        try:
            for table in reversed(Base.metadata.sorted_tables):
                if table.name != "role":
                    await session.execute(delete(table))
            await session.commit()
        finally:
            await session.close()


class SQLAlchemySqliteBackend(AbstractBackend, DatabaseDelete):
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
        self._session_factory = SessionFactorySQLAlchemy(
            database=self.database_url,
        )
        DatabaseDelete.__init__(self, self._session_factory)

    async def create_tables(self) -> None:
        async with self._session_factory.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_defaults_roles(self) -> None:
        async with self.get_uow() as uow:
            await uow.role.create_roles(roles=roles)

    def get_uow(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(
            session_factory=self._session_factory,
            logger=self.logger,
        )

    async def cleare_database(self) -> None:
        session = await self._session_factory()

        try:
            for table in reversed(Base.metadata.sorted_tables):
                if table.name != "role":
                    await session.execute(delete(table))
            await session.commit()
        finally:
            await session.close()
