from sqlalchemy import event, Engine
from logging import Logger
from typing import Sequence, Dict

from sqlite3 import Connection
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.engine import Connection as SQLAlchemyConnection
from sqlalchemy.pool import ConnectionPoolEntry

from domain.exceptions import TableDoesNotExists


async def check_tables_sqlaclhemy_exists(
    engine: AsyncEngine,
    logger: Logger,
    names_tables: Sequence[str],
) -> None:
    # проверяем наличие баз данных в таблице
    def sync_inspect(conn: SQLAlchemyConnection) -> Dict[str, bool]:
        inpector = inspect(conn)
        tables = set(inpector.get_table_names())

        return {table: table in tables for table in names_tables}

    async with engine.begin() as conn:
        tables = await conn.run_sync(sync_inspect)

    result = all(tables.values())
    if result:
        logger.info("The presence of tables has been successfully " "verified. - %s" % names_tables)
        return
    message_error: str = (
        "Not all tables have " "been created - %s\nRun the command to filling the tables"
    )
    logger.error(message_error % tables)
    raise TableDoesNotExists


class SqliteEngineConfigurator:
    def __init__(self, engine: Engine) -> None:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(
            dbapi_connection: Connection,
            connection_record: ConnectionPoolEntry,
        ) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA FOREIGN_KEYS=ON")
            cursor.close()


DATABASE_CONFIGURATOR = {
    "sqlite+aiosqlite": SqliteEngineConfigurator,
    "postgresql+psycopg": None,
}


class DatabaseConnectionConfigurator:
    def __init__(self, driver_name: str, engine: Engine) -> None:
        self.driver_name = driver_name
        self.engine = engine

    def configure_database(self) -> None:
        configurator = DATABASE_CONFIGURATOR.get(self.driver_name, None)
        if configurator is not None:
            configurator(self.engine)
