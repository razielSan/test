import pytest

from app.my_project.backend.presentation.url import ApiMainUrl
from core.constants.error import DigitNotFoundError, LetterNotFoundError
from domain.exceptions import UserAlreadyExists
from dto.exceptions import (
    ErrorResponseDTO,
    ValidationErrorDTO,
)
from dto.user import CreateUserDTO, UserDTO
from test_data.db.redis import RateLimitTestProtocol
from test_data.constants import AppStorageTest


@pytest.mark.api
@pytest.mark.asyncio
async def test_register_user(
    app_storage: AppStorageTest,
):
    username = "test"
    response = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password="123456789abc", username=username).model_dump(),
    )
    assert response.status_code == 200
    user = UserDTO(**response.json())

    assert user.username == username


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_user_already_exists(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    await test_rate_limit_service.clear()

    client = app_storage.client

    username = "test"
    password = "123456789abca"
    response_user_one = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )
    assert response_user_one.status_code == 200

    response_user_two = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )
    exception = UserAlreadyExists()
    assert response_user_two.status_code == exception.status_code

    response = ErrorResponseDTO(**response_user_two.json())

    assert response.code == exception.error.code
    assert response.message == exception.error.message

    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_min_length_password(
    app_storage: AppStorageTest,
):
    username = "test"
    password = "1"
    response_user_one = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json={"username": username, "password": password},
    )
    exception = ValidationErrorDTO()

    assert response_user_one.status_code == exception.status_code

    response = ErrorResponseDTO(**response_user_one.json())
    assert response.code == exception.code
    assert len(response.message) == 1


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_digit_not_found_password(
    app_storage: AppStorageTest,
):
    username = "test"
    password = "qwertyuiopasdf"
    response_user_one = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json={"username": username, "password": password},
    )

    exception = ValidationErrorDTO()

    assert response_user_one.status_code == exception.status_code

    response = ErrorResponseDTO(**response_user_one.json())
    assert response.code == DigitNotFoundError.code
    assert DigitNotFoundError.message in response.message[0]["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_letter_not_found_password(
    app_storage: AppStorageTest,
):
    username = "test"
    password = "12345678910123"
    response_user_one = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json={"username": username, "password": password},
    )
    exception = ValidationErrorDTO()

    assert response_user_one.status_code == exception.status_code

    response = ErrorResponseDTO(**response_user_one.json())
    assert response.code == LetterNotFoundError.code
    assert LetterNotFoundError.message in response.message[0]["message"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_min_length_username(app_storage: AppStorageTest):
    username = "1"
    password = "123456789abc"
    response_user_one = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json={"username": username, "password": password},
    )
    exception = ValidationErrorDTO()

    assert response_user_one.status_code == exception.status_code

    response = ErrorResponseDTO(**response_user_one.json())
    assert response.code == exception.code
    assert len(response.message) == 1


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_min_length_username_and_min_length_password(
    app_storage: AppStorageTest,
):
    username = "1"
    password = "123"
    response_user_one = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json={"username": username, "password": password},
    )
    exception = ValidationErrorDTO()

    assert response_user_one.status_code == exception.status_code

    response = ErrorResponseDTO(**response_user_one.json())
    assert response.code == exception.code
    assert len(response.message) == 2


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_min_length_username_and_digit_not_found_password(
    app_storage: AppStorageTest,
):
    username = "1"
    password = "sdsadasdsasadsadffdf"
    response_user_one = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json={"username": username, "password": password},
    )
    exception = ValidationErrorDTO()

    assert response_user_one.status_code == exception.status_code

    response = ErrorResponseDTO(**response_user_one.json())
    assert response.code == exception.code
    assert len(response.message) == 2


@pytest.mark.api
@pytest.mark.asyncio
async def test_error_min_length_username_and_letter_not_found_password(
    app_storage: AppStorageTest,
):
    username = "1"
    password = "1212323232323232"
    response_user_one = await app_storage.client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json={"username": username, "password": password},
    )
    exception = ValidationErrorDTO()

    assert response_user_one.status_code == exception.status_code
    response = ErrorResponseDTO(**response_user_one.json())
    assert response.code == exception.code
    assert len(response.message) == 2
