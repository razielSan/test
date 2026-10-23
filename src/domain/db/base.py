from typing import Protocol, Optional, Type, Generic, TypeVar
from types import TracebackType
from abc import ABC, abstractmethod

from domain.db.repositories.user import AbsctractUserRepository
from domain.db.repositories.user_role import AbstractUserRoleRepository
from domain.db.repositories.role import AbstractRoleRepository

SessionT = TypeVar("SessionT", covariant=True)


class SessionFactoryProtocol(Protocol, Generic[SessionT]):
    async def __call__(self) -> SessionT:
        pass


class UnitOfWorkProtocol(Protocol):
    user: AbsctractUserRepository
    role: AbstractRoleRepository
    user_role: AbstractUserRoleRepository

    async def __aenter__(self) -> "UnitOfWorkProtocol":
        pass

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        pass


class AbstractBackend(ABC):
    @abstractmethod
    async def create_tables(self) -> None:
        pass

    @abstractmethod
    async def create_defaults_roles(self) -> None:
        pass

    @abstractmethod
    def get_uow(self) -> UnitOfWorkProtocol:
        pass

    @abstractmethod
    async def cleare_database(self) -> None:
        pass


class AbstactRateLimitClient(ABC):
    @abstractmethod
    async def increasing_the_attempt_counter_user_ip(
        self,
        ip: str,
    ) -> int:
        pass

    @abstractmethod
    async def increasing_the_attempt_counter_user_name(
        self,
        name: str,
    ) -> int:
        pass

    @abstractmethod
    async def setting_a_time_limit_user_ip(
        self,
        ip: str,
        seconds: int,
    ) -> None:
        pass

    @abstractmethod
    async def setting_a_time_limit_user_name(
        self,
        name: str,
        seconds: int,
    ) -> None:
        pass

    @abstractmethod
    async def get_number_of_attempts_user_ip(self, ip: str) -> int:
        pass

    @abstractmethod
    async def get_number_of_attempts_user_name(self, name: str) -> int:
        pass

    @abstractmethod
    async def clear_database(self) -> None:
        pass

    @abstractmethod
    async def close_connection(self) -> None:
        pass
