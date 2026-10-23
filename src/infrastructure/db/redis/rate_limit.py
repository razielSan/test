from redis import asyncio as aioredis

from domain.db.base import AbstactRateLimitClient
from settings.config import settings


class RateLimitRedisClient(AbstactRateLimitClient):
    def __init__(self) -> None:
        self.client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
        self.login = "login:attempts:ip"
        self.user = "login:attempts:user"

    async def increasing_the_attempt_counter_user_ip(
        self,
        ip: str,
    ) -> int:
        counter: int = await self.client.incr(f"{self.login}:{ip}")
        return counter

    async def increasing_the_attempt_counter_user_name(
        self,
        name: str,
    ) -> int:
        counter: int = await self.client.incr(f"{self.user}:{name}")
        return counter

    async def setting_a_time_limit_user_ip(
        self,
        ip: str,
        seconds: int,
    ) -> None:
        await self.client.expire(f"{self.login}:{ip}", seconds)

    async def setting_a_time_limit_user_name(
        self,
        name: str,
        seconds: int,
    ) -> None:
        await self.client.expire(f"{self.user}:{name}", seconds)

    async def get_number_of_attempts_user_ip(self, ip: str) -> int:
        number = await self.client.get(f"{self.login}:{ip}")
        if number is None:
            return 0
        return int(number)

    async def get_number_of_attempts_user_name(self, name: str) -> int:
        number = await self.client.get(f"{self.user}:{name}")
        if number is None:
            return 0
        return int(number)

    async def clear_database(self) -> None:
        await self.client.flushdb()

    async def close_connection(self) -> None:
        await self.client.aclose()
