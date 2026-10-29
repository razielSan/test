from abc import ABC, abstractmethod
from typing import Optional

from domain.db.models.user import UserDOMAIN


class AbsctractUserRepository(ABC):
    @abstractmethod
    async def create_user(
        self,
        username: str,
        password_hash: str,
    ) -> UserDOMAIN:
        pass

    @abstractmethod
    async def get_user(self, username: str) -> Optional[UserDOMAIN]:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[UserDOMAIN]:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> int:
        pass

    @abstractmethod
    async def update_username(
        self,
        user_id: int,
        username: str,
    ) -> UserDOMAIN:
        pass

    @abstractmethod
    async def update_password(
        self,
        user_id: int,
        password_hash: str,
    ) -> UserDOMAIN:
        pass
