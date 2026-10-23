from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.engine.url import make_url

from domain.db.base import SessionFactoryProtocol
from infrastructure.db.sqlalchemy.utils import DatabaseConnectionConfigurator


class SessionFactorySQLAlchemy(SessionFactoryProtocol[AsyncSession]):
    def __init__(
        self,
        database: str,
    ) -> None:
        self.database = database

        self.engine = create_async_engine(
            url=database,
            pool_size=5,
            echo=False,
            max_overflow=10,
        )

        self.session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        self._url = make_url(self.database)
        self._database_configurator = DatabaseConnectionConfigurator(
            driver_name=self._url.drivername, engine=self.engine.sync_engine
        )
        self._database_configurator.configure_database()

    async def __call__(self) -> AsyncSession:
        return self.session()
