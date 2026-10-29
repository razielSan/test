import pytest

from domain.db.base import UnitOfWorkProtocol
from infrastructure.security.hash import ArgonHasher


@pytest.mark.integration
@pytest.mark.asyncio
async def test_password_hashed(test_uow: UnitOfWorkProtocol):
    password = "123456789вснвыв"
    username = "test user"
    hasher = ArgonHasher()
    hashed_password = hasher.hash(password=password)
    async with test_uow as uow:
        user = await uow.user.create_user(password_hash=hashed_password, username=username)

    assert user.password_hash != password
    assert hasher.verify(
        password_hash=hashed_password,
        password=password,
    )
