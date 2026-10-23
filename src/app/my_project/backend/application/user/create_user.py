from dto.user import UserDTO, CreateUserDTO
from domain.db.models.user import UserDOMAIN
from domain.security.hasher import PasswordHasherProtocol
from domain.db.base import UnitOfWorkProtocol


class CreateUser:
    def __init__(
        self,
        uow: UnitOfWorkProtocol,
        hasher: PasswordHasherProtocol,
    ) -> None:
        self.uow = uow
        self.hasher: PasswordHasherProtocol = hasher

    async def execute(self, user: CreateUserDTO, role_name: str = "user") -> UserDTO:
        password_hash = self.hasher.hash(password=user.password)
        async with self.uow as uow:
            user_success: UserDOMAIN = await uow.user.create_user(
                username=user.username, password_hash=password_hash
            )
            role = await uow.role.get_by_name(name=role_name)
            await uow.user_role.add(
                user_id=user_success.id,
                role_id=role.id,
            )
        return UserDTO(
            id=user_success.id,
            username=user_success.username,
            is_active=user_success.is_active,
        )
