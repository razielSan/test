from getpass import getpass
from logging import getLogger
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from pydantic import ValidationError

from app.my_project.backend.application.user.create_user import CreateUser
from domain.exceptions import UserAlreadyExists
from domain.db.constants import Role
from dto.user import CreateUserDTO
from settings.config import settings
from infrastructure.db.settings import DatabaseConfig
from infrastructure.security.hash import ArgonHasher


async def main() -> None:
    username = input("Username: ")
    password = getpass("Password: ")
    password_repeat = getpass("Repeat_password: ")

    if password != password_repeat:
        print("password do not match")
        return

    logger = getLogger(name=__name__)
    database_config = DatabaseConfig(
        logger=logger,
        database_url=settings.DATABASE_CONNECT,
    )
    try:
        uow = database_config.uow

        await CreateUser(uow=uow, hasher=ArgonHasher()).execute(
            user=CreateUserDTO(password=password, username=username),
            role_name=Role.admin.value,
        )
    except ValidationError as err:
        print(err)
    except UserAlreadyExists:
        print("Initial admin user already exists")
    else:
        print("Initial admin user created")


def cli() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    cli()
