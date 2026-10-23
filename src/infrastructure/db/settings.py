from logging import Logger

from domain.exceptions import NameDoesNotExists, AdminDoesNotInizialized
from domain.db.constants import names_tables, roles, Role
from infrastructure.db.sqlalchemy.session import SessionFactorySQLAlchemy
from infrastructure.db.sqlalchemy.uow import SQLAlchemyUnitOfWork
from infrastructure.db.utils import check_tables_sqlaclhemy_exists


class DatabaseConfig:
    def __init__(
        self,
        logger: Logger,
        database_url: str,
    ) -> None:
        self._logger = logger
        self._session_factory = SessionFactorySQLAlchemy(
            database=database_url,
        )

    @property
    def session_factory(self) -> SessionFactorySQLAlchemy:
        return self._session_factory

    @property
    def uow(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(
            session_factory=self._session_factory,
            logger=self._logger,
        )

    async def check_required_roles(
        self,
    ) -> None:
        async with self.uow as uow:
            result = await uow.role.all_roles_exists(roles=roles)
            if not result:
                self._logger.error(
                    "Not all role names were successfully created."
                    "\nRun the database creation command or start mirgations."
                )

                raise NameDoesNotExists
            self._logger.info("The roles were successfully initialized.")

    async def check_admin_exists(self) -> None:
        async with self.uow as uow:
            role = await uow.role.get_by_name(name=Role.admin.value)
            user = await uow.user_role.get_users(role_id=role.id)
            if not user:
                self._logger.info(
                    "The administrator was not initialized. "
                    "Run the command to create an administrator"
                )
                raise AdminDoesNotInizialized
            self._logger.info("The admin was successfully initialized.")

    async def check_database(
        self,
    ) -> None:
        await check_tables_sqlaclhemy_exists(
            engine=self.session_factory.engine,
            logger=self._logger,
            names_tables=names_tables,
        )
