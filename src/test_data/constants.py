from enum import Enum

from dataclasses import dataclass
from fastapi import FastAPI
from httpx import AsyncClient


class IpClientTest(str, Enum):
    host = "127.0.0.10"
    port = "5000"


@dataclass
class AppStorageTest:
    client: AsyncClient
    app: FastAPI


TEST_ALLOWED_ORIGINS = ("http://test",)
TEST_TRUSTED_PROXIES = (
    IpClientTest.host.value,
    "127.0.0.222",
)
TEST_ALLOWED_REDIRECT_URLS = ("/test", "/test/user")
