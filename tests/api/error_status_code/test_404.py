import pytest

from dto.exceptions import NotFoundPageDTO, ErrorResponseDTO
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_404_by_page(app_storage: AppStorageTest):
    response = await app_storage.client.get("/Test")

    ip_not_found = NotFoundPageDTO()
    assert 'alt="not found"' in response.text
    assert response.status_code == ip_not_found.status_code


@pytest.mark.api
@pytest.mark.asyncio
async def test_404_by_api(app_storage: AppStorageTest):
    response = await app_storage.client.get("/api/test")

    ip_not_found = NotFoundPageDTO()

    assert response.status_code == ip_not_found.status_code

    exception = ErrorResponseDTO(**response.json())

    assert exception.code == ip_not_found.content["code"]
    assert exception.message == ip_not_found.content["message"]
