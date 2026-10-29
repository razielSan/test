# import pytest
# from pytest_mock import MockerFixture

# from app.my_project.backend.presentation.url import ApiMainUrl
# from domain.exceptions import IpNotFoundError
# from dto.exceptions import ErrorResponseDTO
# from test_data.constants import AppStorageTest


# @pytest.mark.asyncio
# @pytest.mark.api
# async def test_ip_not_found(
#     app_storage: AppStorageTest,
#     mocker: MockerFixture,
# ):
#     mock_host = mocker.patch("fastapi.Request.client", create=True)
#     mock_host.host = None

#     response = await app_storage.client.post(
#         f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
#         data={
#             "username": "name",
#             "password": "123456abcdefabc",
#         },
#     )

#     ip_not_found = IpNotFoundError()
#     assert response.status_code == ip_not_found.status_code

#     exception = ErrorResponseDTO(**response.json())
#     assert exception.message == ip_not_found.error.message
#     assert exception.code == ip_not_found.error.code
