import pytest
import asyncio

from httpx import AsyncClient

from app.my_project.backend.presentation.url import ApiMainUrl
from domain.exceptions import AuthenticatedError, RateLimitError
from core.constants.user import TokenName
from dto.user import CreateUserDTO
from dto.exceptions import ErrorResponseDTO
from test_data.constants import IpClientTest, TEST_TRUSTED_PROXIES, AppStorageTest
from test_data.db.redis import RateLimitTestProtocol


async def checking_for_an_increase_in_counter_for_auth(
    username: str,
    password: str,
    client: AsyncClient,
    ip: str,
    test_rate_limit_service,
    total_counter: int,
    check_counter=True,
):
    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": username,
            "password": password,
        },
        headers={"X-Forwarded-For": ip},
    )

    exception = AuthenticatedError()
    assert response_authenticate.status_code == exception.status_code

    counter = await test_rate_limit_service.get_numbers_of_attempts(ip=ip, name=username)
    if check_counter:
        assert counter.ip_counter == total_counter
        assert counter.name_counter == total_counter


@pytest.mark.api
@pytest.mark.asyncio
async def test_rate_limter_0(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    client = app_storage.client

    username = "test user1"
    password = "test_password12345678"

    counter = await test_rate_limit_service.get_numbers_of_attempts(
        name=username, ip=IpClientTest.host.value
    )
    assert counter.ip_counter == 0
    assert counter.name_counter == 0

    # проверка на успешность auth с 0 счетчиком
    response = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(password=password, username=username).model_dump(),
    )
    assert response.status_code == 200

    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": username,
            "password": password,
        },
    )

    counter = await test_rate_limit_service.get_numbers_of_attempts(
        name=username,
        ip=IpClientTest.host.value,
    )
    assert response_authenticate.status_code == 204

    # счетчик после запроса не изменился
    assert counter.ip_counter == 0
    assert counter.name_counter == 0

    # cookies созданы
    assert isinstance(client.cookies.get(TokenName.ACCESS_TOKEN.value), str)
    assert isinstance(client.cookies.get(TokenName.REFRESH_TOKEN.value), str)

    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_rate_limter_1(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    client = app_storage.client

    correct_username = "test user"
    correct_password = "test_password12345678"

    response = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.REGISTER_USER}",
        json=CreateUserDTO(
            password=correct_password,
            username=correct_username,
        ).model_dump(),
    )
    assert response.status_code == 200

    invalid_username = "1"
    invalid_password = "2"
    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": invalid_username,
            "password": invalid_password,
        },
    )
    exception = AuthenticatedError()
    assert response_authenticate.status_code == exception.status_code

    counter = await test_rate_limit_service.get_numbers_of_attempts(
        ip=IpClientTest.host.value, name=invalid_username
    )
    assert counter.ip_counter == 1
    assert counter.name_counter == 1
    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_rate_limter_attempts_1_through_6(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    client = app_storage.client

    username = "1"
    password = "1"
    for index in range(1, 6):
        await checking_for_an_increase_in_counter_for_auth(
            username=username,
            password=password,
            client=client,
            ip=TEST_TRUSTED_PROXIES[1],
            total_counter=index,
            test_rate_limit_service=test_rate_limit_service,
        )

    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": username,
            "password": password,
        },
    )
    exception = RateLimitError()
    assert response_authenticate.status_code == exception.status_code
    response = ErrorResponseDTO(**response_authenticate.json())

    # После превышения лимита попыток, доступ ограничен до истечения времени
    assert response.code == exception.error.code
    assert response.message == exception.error.message

    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_limit_TTL(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    client = app_storage.client

    username = "1"
    password = "1"
    for index in range(1, 6):
        await checking_for_an_increase_in_counter_for_auth(
            username=username,
            password=password,
            client=client,
            ip=TEST_TRUSTED_PROXIES[1],
            total_counter=index,
            test_rate_limit_service=test_rate_limit_service,
        )

    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": username,
            "password": password,
        },
        headers={"X-Forwarded-For": TEST_TRUSTED_PROXIES[1]},
    )
    exception = RateLimitError()
    assert response_authenticate.status_code == exception.status_code
    response = ErrorResponseDTO(**response_authenticate.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message

    await asyncio.sleep(1)

    counter = await test_rate_limit_service.get_numbers_of_attempts(
        ip=TEST_TRUSTED_PROXIES[1], name=username
    )

    # счетчики сбрасываются по истечении времени
    assert counter.ip_counter == 0
    assert counter.name_counter == 0

    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_ip_separately_from_username(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    client = app_storage.client

    username = "1"
    password = "test_password12345678"

    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": username,
            "password": password,
        },
    )

    exception = AuthenticatedError()
    assert response_authenticate.status_code == exception.status_code

    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": "2",
            "password": password,
        },
    )

    assert response_authenticate.status_code == exception.status_code

    counter = await test_rate_limit_service.get_numbers_of_attempts(
        ip=IpClientTest.host.value, name=username
    )

    # счетчики ip и username различны
    assert counter.ip_counter == 2
    assert counter.name_counter == 1

    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_counter_limit_by_username(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    client = app_storage.client

    ips = [
        TEST_TRUSTED_PROXIES[0],
        TEST_TRUSTED_PROXIES[1],
        TEST_TRUSTED_PROXIES[1],
        TEST_TRUSTED_PROXIES[1],
        TEST_TRUSTED_PROXIES[1],
    ]
    username = "1"
    password = "1"
    for counter, ip in enumerate(ips, start=1):
        await checking_for_an_increase_in_counter_for_auth(
            username=username,
            password=password,
            client=client,
            ip=ip,
            total_counter=counter,
            test_rate_limit_service=test_rate_limit_service,
            check_counter=False,
        )

    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": username,
            "password": password,
        },
        headers={"X-Forwarded-For": TEST_TRUSTED_PROXIES[1]},
    )
    exception = RateLimitError()
    assert response_authenticate.status_code == exception.status_code
    response = ErrorResponseDTO(**response_authenticate.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message

    counter = await test_rate_limit_service.get_numbers_of_attempts(ip=ip, name=username)

    #  Один username с другого IP всё равно ограничивается по username.
    assert counter.ip_counter == 4
    assert counter.name_counter == 5
    await test_rate_limit_service.shutdown()


@pytest.mark.api
@pytest.mark.asyncio
async def test_counter_limit_by_ip(
    app_storage: AppStorageTest,
    test_rate_limit_service: RateLimitTestProtocol,
):
    client = app_storage.client

    name = "2"
    names = [
        "1",
        name,
        name,
        name,
        name,
    ]
    password = "1"
    for counter, username in enumerate(names, start=1):
        await checking_for_an_increase_in_counter_for_auth(
            username=username,
            password=password,
            client=client,
            ip=TEST_TRUSTED_PROXIES[1],
            total_counter=counter,
            test_rate_limit_service=test_rate_limit_service,
            check_counter=False,
        )

    response_authenticate = await client.post(
        f"{ApiMainUrl.PREFIX}{ApiMainUrl.AUTHENTICATE_USER}",
        data={
            "username": name,
            "password": password,
        },
        headers={"X-Forwarded-For": TEST_TRUSTED_PROXIES[1]},
    )
    exception = RateLimitError()
    assert response_authenticate.status_code == exception.status_code
    response = ErrorResponseDTO(**response_authenticate.json())
    assert response.code == exception.error.code
    assert response.message == exception.error.message

    counter = await test_rate_limit_service.get_numbers_of_attempts(
        ip=TEST_TRUSTED_PROXIES[1],
        name=name,
    )

    #  Другой username с того же IP ограничивается по IP.
    assert counter.ip_counter == 5
    assert counter.name_counter == 4

    await test_rate_limit_service.shutdown()

    assert 1 == 18