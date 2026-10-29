from typing import Union, Type
from dataclasses import dataclass

from test_data.db.sqlalchemy import SQLAlchemySqliteBackend, SQLAlchemyBackend
from test_data.settings import test_settings
from test_data.paths import test_database_url


@dataclass
class StorageBackend:
    path: str
    backend: Union[Type[SQLAlchemyBackend], Type[SQLAlchemySqliteBackend]]


DATABASE_BACKENDS = {
    test_settings.SQLITE_NAME_DATABASE: StorageBackend(
        path=test_database_url.TEST_SQLITE_URL,
        backend=SQLAlchemySqliteBackend,
    ),
    test_settings.POSTGRESQL_NAME_DATABASE: StorageBackend(
        path=test_database_url.TEST_POSTGRESQL_URL,
        backend=SQLAlchemyBackend,
    ),
}


def get_backends(
    type_database: str,
) -> Union[SQLAlchemyBackend, SQLAlchemySqliteBackend]:
    storage_backend = DATABASE_BACKENDS[type_database]
    path = storage_backend.path
    backend = storage_backend.backend
    return backend(path)
