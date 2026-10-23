from abc import ABC, abstractmethod
from typing import List

from domain.db.models.role import RoleDOMAIN
from domain.db.models.user import UserDOMAIN


class AbstractUserRoleRepository(ABC):
    @abstractmethod
    async def add(self, user_id: int, role_id: int) -> None:
        pass

    @abstractmethod
    async def get_roles(self, user_id: int) -> List[RoleDOMAIN]:
        pass

    @abstractmethod
    async def get_users(self, role_id: int) -> List[UserDOMAIN]:
        pass
