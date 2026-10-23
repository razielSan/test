from fastapi import APIRouter, Depends

from app.my_project.backend.application.user.get_user import GetUser
from app.my_project.backend.presentation.dependencies import (
    get_uow,
    require_admin,
)
from app.my_project.backend.presentation.url import ApiAdminUrl
from dto.user import UserDTO
from domain.db.base import UnitOfWorkProtocol


router = APIRouter(prefix=ApiAdminUrl.PREFIX, tags=["admin"])


@router.get(
    path=ApiAdminUrl.ADMIN_GET_USER,
    dependencies=[
        Depends(require_admin),
    ],
)
async def admin_get_user(
    user_id: int,
    uow: UnitOfWorkProtocol = Depends(get_uow),
) -> UserDTO:
    result_user = await GetUser(uow=uow).execute(user_id=user_id)
    return result_user
