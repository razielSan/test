from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from settings.paths import ROOT_DIR


class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    SECRET_KEY_TOKEN: str
    SECRET_KEY_TOKEN_REFRESH: str
    ALGORITHM_TOKEN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    DATABASE_CONNECT: str

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
    )


settings = Settings()
