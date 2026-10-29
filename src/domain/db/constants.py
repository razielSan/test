from enum import Enum


class DatabaseName(str, Enum):
    sqlalchemy_sqlite = "sqlite"
    sqlalchemy_postgresql = "postgresql"


class DriverName(str, Enum):
    asyncpg = "asyncpg"
    psycopg = "psycopg"
    aiosqlite = "aiosqlite"


names_drivers = {driver.value for driver in DriverName}
names_databases = {database.value for database in DatabaseName}


CORRECT_URL_DATABASE = f"{DatabaseName.sqlalchemy_sqlite.value}+{DriverName.aiosqlite.value}://"

SUPPORTED_DATABASE_DRIVERS = {
    DatabaseName.sqlalchemy_sqlite: {DriverName.aiosqlite},
    DatabaseName.sqlalchemy_postgresql: {
        DriverName.asyncpg,
        DriverName.psycopg,
    },
}

CORRECT_URL_DATABASE = f"{DatabaseName.sqlalchemy_sqlite.value}+{DriverName.aiosqlite.value}://"


class TableName(str, Enum):
    role = "role"
    user = "user"
    user_role = "user_role"


class Role(str, Enum):
    admin = "admin"
    user = "user"


roles = [role.value for role in Role]


names_tables = [table.value for table in TableName]
