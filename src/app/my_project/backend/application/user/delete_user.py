from dto.user import UserDTO
from domain.db.base import UnitOfWorkProtocol


class DeleteUser:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
    ) -> None:
        self.uow = uow

    async def execute(self, user: UserDTO) -> UserDTO:
        async with self.uow as uow:
            deleted_id = await uow.user.delete_user(
                user_id=user.id,
            )
        return UserDTO(id=deleted_id, username=user.username, is_active=user.is_active)
