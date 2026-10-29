from abc import ABC, abstractmethod
from typing import Sequence

from domain.db.models.role import RoleDOMAIN


class AbstractRoleRepository(ABC):
    @abstractmethod
    async def create_roles(self, roles: Sequence[str]) -> None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> RoleDOMAIN:
        pass

    @abstractmethod
    async def all_roles_exists(self, roles: Sequence[str]) -> bool:
        pass
