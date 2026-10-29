import asyncio
import sys
from sqlite3 import OperationalError
import logging

from infrastructure.db.sqlalchemy.session import SessionFactorySQLAlchemy
from domain.db.constants import roles
from infrastructure.db.sqlalchemy.repositories.role import SqlAlchemyRoleRepository
from settings.config import settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main() -> None:
    logger = logging.getLogger(name=__name__)
    session_factory = SessionFactorySQLAlchemy(
        database=settings.DATABASE_CONNECT,
    )
    session = await session_factory()
    try:
        await SqlAlchemyRoleRepository(
            session=session,
            logger=logger,
        ).create_roles(roles=roles)
        print("The role names have been successfully created.")
        await session.commit()
    except OperationalError as err:
        print(err)
        await session.rollback()
    finally:
        await session.close()


def cli() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    cli()
