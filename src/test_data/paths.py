from __future__ import annotations
from pathlib import Path
from sqlalchemy.engine import make_url

from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.paths import ROOT_DIR


class TestDataBaseUrl(BaseSettings):
    TEST_POSTGRESQL_URL: str = "database_name+driver_name://...."
    TEST_SQLITE_URL: str = "database_name+driver_name://...."

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env.test",
    )

    @property
    def delete_test_sqlite_path(self) -> Path:
        return ROOT_DIR / Path(make_url(self.TEST_SQLITE_URL).database)


test_database_url = TestDataBaseUrl()
