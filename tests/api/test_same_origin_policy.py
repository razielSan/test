import pytest

from app.my_project.backend.presentation.url import ApiMainUrl
from domain.exceptions import OriginError, RefererError
from dto.user import CreateUserDTO
from dto.exceptions import ErrorResponseDTO
from test_data.constants import TEST_ALLOWED_ORIGINS, AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "null",
        "http://evil.com",
        f"{TEST_ALLOWED_ORIGINS[0]}/evil/evil.com",
    ],
)
async def test_origin_policy_403_error(
    app_storage: AppStorageTest,
    url: str,
) -> None:
    username = "test"
    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password="123456789abc", username=username).model_dump(),
        headers={"Origin": url},
    )

    exception = OriginError()
    assert response.status_code == exception.status_code
    error_origin = ErrorResponseDTO(**response.json())
    assert error_origin.code == exception.error.code
    assert error_origin.message == exception.error.message


@pytest.mark.api
@pytest.mark.asyncio
async def test_headers_referer_success(app_storage: AppStorageTest) -> None:
    username = "test"
    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(
            password="123456789abc",
            username=username,
        ).model_dump(),
        headers={"Origin": "", "Referer": f"{TEST_ALLOWED_ORIGINS[0]}/evil.com"},
    )
    assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "null",
        "http://evil.com",
        "",
    ],
)
async def test_headers_referer_403_error(app_storage: AppStorageTest, url: str) -> None:
    username = "test"
    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password="123456789abc", username=username).model_dump(),
        headers={"Origin": "", "Referer": url},
    )
    exception = RefererError()
    assert response.status_code == 403
    assert response.status_code == exception.status_code
    error_origin = ErrorResponseDTO(**response.json())
    assert error_origin.code == exception.error.code
    assert error_origin.message == exception.error.message
