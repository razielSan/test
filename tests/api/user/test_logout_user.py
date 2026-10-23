import pytest

from app.my_project.backend.presentation.url import ApiMainUrl
from core.constants.user import TokenName, ResponseMessageUser
from dto.user import CreateUserDTO
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_logout_user(app_storage: AppStorageTest) -> None:
    assert app_storage.client.cookies.get(name=TokenName.ACCESS_TOKEN.value) is None
    assert app_storage.client.cookies.get(name=TokenName.REFRESH_TOKEN.value) is None

    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(
            username="test user",
            password="1234567890asd",
        ).model_dump(),
    )
    assert response.status_code == 200
    assert isinstance(app_storage.client.cookies.get(name=TokenName.ACCESS_TOKEN.value), str)
    assert isinstance(app_storage.client.cookies.get(name=TokenName.REFRESH_TOKEN.value), str)

    response_logout_user = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.LOGOUT_USER}",
    )
    assert response_logout_user.status_code == 200

    assert response_logout_user.cookies.get(TokenName.ACCESS_TOKEN.value, None) is None
    assert response_logout_user.cookies.get(TokenName.REFRESH_TOKEN.value, None) is None
    assert app_storage.client.cookies.get(name=TokenName.ACCESS_TOKEN.value) is None
    assert app_storage.client.cookies.get(name=TokenName.REFRESH_TOKEN.value) is None

    assert ResponseMessageUser.LOGOUT_SUCCESS == response_logout_user.json()
