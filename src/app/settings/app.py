from infrastructure.security.url import BaseAppURL


class Settings:
    APP: str = "app.main:app"
    HOST: str = BaseAppURL.HOST
    PORT: int = BaseAppURL.PORT
    RELOAD: bool = True


settings = Settings()
