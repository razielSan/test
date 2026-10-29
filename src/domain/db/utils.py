from typing import Set

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError, NoSuchModuleError

from core.constants.error import (
    InvalidDatabaseUrl,
    DriverNotSupported,
    DatabaseNameNotSupported,
    DriverNotSupportedDatabase,
)
from domain.db.constants import CORRECT_URL_DATABASE, names_drivers, names_databases
from domain.db.constants import SUPPORTED_DATABASE_DRIVERS, DatabaseName, DriverName


def validate_database_name_and_driver(url: str) -> None:
    try:
        parsed_url = make_url(name_or_url=url)
    except ArgumentError as err:
        raise ValueError(
            InvalidDatabaseUrl.message % (url, CORRECT_URL_DATABASE),
        ) from err

    try:
        driver_name = parsed_url.get_driver_name()
        database_name = parsed_url.get_backend_name()
    except NoSuchModuleError as err:
        raise ValueError(
            InvalidDatabaseUrl.message % (url, CORRECT_URL_DATABASE),
        ) from err

    try:
        DriverName(driver_name)
    except ValueError as err:
        raise ValueError(
            DriverNotSupported.message % (driver_name, names_drivers),
        ) from err

    try:
        database = DatabaseName(database_name)
    except ValueError as err:
        raise ValueError(
            DatabaseNameNotSupported.message % (database_name, names_databases),
        ) from err

    supported_drivers = SUPPORTED_DATABASE_DRIVERS[database]
    if driver_name not in supported_drivers:
        drivers: Set[str] = {driver.value for driver in supported_drivers}
        raise ValueError(
            DriverNotSupportedDatabase.message
            % (
                database_name,
                drivers,
            )
        )
