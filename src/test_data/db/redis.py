from typing import Protocol

from logging import Logger

from app.my_project.backend.application.services.rate_limit import RateLimitService
from domain.db.base import AbstactRateLimitClient
from dto.user import AttemptCounterDTO


class RateLimitTestProtocol(Protocol):
    async def clear(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def get_numbers_of_attempts(self, name: str, ip: str) -> AttemptCounterDTO:
        pass


class RateLimiTestService(RateLimitService):
    def __init__(
        self,
        rate_limiter: AbstactRateLimitClient,
        logger: Logger,
        max_name_counter: int,
        max_ip_counter: int,
        time_limit: int,
    ):
        super().__init__(
            rate_limiter=rate_limiter,
            logger=logger,
            max_name_counter=max_name_counter,
            max_ip_counter=max_ip_counter,
            time_limit=time_limit,
        )

    async def clear(self) -> None:
        await self.rate_limiter.clear_database()

    async def shutdown(self) -> None:
        await self.rate_limiter.clear_database()
        await self.rate_limiter.close_connection()

    async def get_numbers_of_attempts(self, name: str, ip: str) -> AttemptCounterDTO:
        name_counter = await self.rate_limiter.get_number_of_attempts_user_name(name=name)
        ip_counter = await self.rate_limiter.get_number_of_attempts_user_ip(
            ip=ip,
        )
        return AttemptCounterDTO(
            ip_counter=ip_counter,
            name_counter=name_counter,
        )
