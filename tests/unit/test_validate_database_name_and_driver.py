import pytest

from core.constants.error import (
    InvalidDatabaseUrl,
    DriverNotSupported,
    DatabaseNameNotSupported,
    DriverNotSupportedDatabase,
)
from domain.db.utils import validate_database_name_and_driver
from domain.db.constants import (
    CORRECT_URL_DATABASE,
    DriverName,
    DatabaseName,
    names_databases,
    names_drivers,
    SUPPORTED_DATABASE_DRIVERS,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    (
        f"{DatabaseName.sqlalchemy_postgresql.value}+{DriverName.asyncpg.value}://////",
        f"{DatabaseName.sqlalchemy_postgresql.value}+{DriverName.asyncpg.value}://......",
        f"{DatabaseName.sqlalchemy_postgresql.value}+{DriverName.asyncpg.value}://+!-*#",
        f"{DatabaseName.sqlalchemy_postgresql.value}+{DriverName.psycopg.value}://////",
        f"{DatabaseName.sqlalchemy_postgresql.value}+{DriverName.psycopg.value}://......",
        f"{DatabaseName.sqlalchemy_postgresql.value}+{DriverName.psycopg.value}://+!-*#",
        f"{DatabaseName.sqlalchemy_sqlite.value}+{DriverName.aiosqlite.value}://////",
        f"{DatabaseName.sqlalchemy_sqlite.value}+{DriverName.aiosqlite.value}:///......",
        f"{DatabaseName.sqlalchemy_sqlite.value}+{DriverName.aiosqlite.value}:///+!-*#",
    ),
)
def test_validate_database_name_and_driver_accepts_supported_pair(url):
    validate_database_name_and_driver(url=url)


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    (
        "test",
        "database_name:///",
        "database_name+driver_name:/",
        "database_name+driver_name:",
        "database_name+driver_name+++",
        "database_name+driver_name:/---/",
    ),
)
def test_invalid_base_url(url):
    with pytest.raises(ValueError) as exc_info:
        validate_database_name_and_driver(url=url)

    assert InvalidDatabaseUrl.message % (url, CORRECT_URL_DATABASE) in str(exc_info.value)


@pytest.mark.unit
def test_driver_not_supported():
    driver_name = "tedt_driver"
    url = f"{DatabaseName.sqlalchemy_sqlite.value}+{driver_name}:///...."

    assert driver_name not in [driver.value for driver in DriverName]

    with pytest.raises(ValueError) as exc_info:
        validate_database_name_and_driver(url=url)

    assert DriverNotSupported.message % (driver_name, names_drivers) in str(exc_info.value)


@pytest.mark.unit
def test_database_not_supported():
    database_name = "tedt_database"
    url = f"{database_name}+{DriverName.psycopg.value}:///...."

    assert database_name not in [database.value for database in DatabaseName]

    with pytest.raises(ValueError) as exc_info:
        validate_database_name_and_driver(url=url)

    assert DatabaseNameNotSupported.message % (database_name, names_databases) in str(
        exc_info.value
    )


@pytest.mark.unit
def test_driver_not_supported_database():
    database = DatabaseName.sqlalchemy_postgresql
    driver = DriverName.aiosqlite
    url = f"{database.value}+{driver.value}:///...."

    with pytest.raises(ValueError) as exc_info:
        validate_database_name_and_driver(url=url)

    drivers = SUPPORTED_DATABASE_DRIVERS[database]
    names_drivers = {driver.value for driver in drivers}
    assert DriverNotSupportedDatabase.message % (database.value, names_drivers) in str(
        exc_info.value
    )


@pytest.mark.unit
def test_driver_not_supported_sqlite_default_pysqlite():
    url = "sqlite://"

    with pytest.raises(ValueError) as exc_info:
        validate_database_name_and_driver(url=url)

    driver_name = "pysqlite"
    assert DriverNotSupported.message % (driver_name, names_drivers) in str(exc_info.value)
