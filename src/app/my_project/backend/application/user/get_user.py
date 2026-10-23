from dto.user import UserDTO
from domain.db.base import UnitOfWorkProtocol
from domain.exceptions import UserNotFound


class GetUser:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
    ) -> None:
        self.uow = uow

    async def execute(self, user_id: int) -> UserDTO:
        async with self.uow as uow:
            user = await uow.user.get_user_by_id(user_id=user_id)
            if user is None:
                raise UserNotFound(user_id=user_id)
        return UserDTO(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
        )
