from logging import Logger
from typing import Sequence, Dict

from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from domain.exceptions import TableDoesNotExists


async def check_tables_sqlaclhemy_exists(
    engine: AsyncEngine,
    logger: Logger,
    names_tables: Sequence[str],
) -> None:
    # проверяем наличие баз данных в таблице
    def sync_inspect(conn: Connection) -> Dict[str, bool]:
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
