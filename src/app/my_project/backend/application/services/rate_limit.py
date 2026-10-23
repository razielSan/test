from typing import Protocol
from logging import Logger

from domain.db.base import AbstactRateLimitClient
from domain.exceptions import RateLimitError
from dto.user import AttemptCounterDTO


class RateLimitServiceProtocol(Protocol):
    async def check_login(
        self,
        ip: str,
        name: str,
    ) -> None:
        pass

    async def increase_the_attempt_counter(self, ip: str, name: str) -> AttemptCounterDTO:
        pass

    async def setting_time_limit(
        self,
        ip: str,
        name: str,
        attempt_counter: AttemptCounterDTO,
        time_limit: int = 60,
    ) -> None:
        pass


class RateLimitService:
    def __init__(
        self,
        rate_limiter: AbstactRateLimitClient,
        logger: Logger,
        max_name_counter: int,
        max_ip_counter: int,
        time_limit: int,
    ) -> None:
        self.logger: Logger = logger
        self.rate_limiter = rate_limiter
        self.max_name_counter = max_name_counter
        self.max_ip_counter = max_ip_counter
        self.time_limit = time_limit

    async def check_login(
        self,
        ip: str,
        name: str,
    ) -> None:
        ip_counter = await self.rate_limiter.get_number_of_attempts_user_ip(
            ip=ip,
        )
        name_counter = await self.rate_limiter.get_number_of_attempts_user_name(name=name)
        if name_counter >= self.max_name_counter or ip_counter >= self.max_ip_counter:
            self.logger.warning(f"RATE LIMIT ERROR\nip - {ip}\n{name} - username")
            raise RateLimitError()

    async def increase_the_attempt_counter(
        self,
        ip: str,
        name: str,
    ) -> AttemptCounterDTO:
        ip_counter = await self.rate_limiter.increasing_the_attempt_counter_user_ip(
            ip=ip,
        )
        name_counter = await self.rate_limiter.increasing_the_attempt_counter_user_name(
            name=name,
        )
        return AttemptCounterDTO(
            ip_counter=ip_counter,
            name_counter=name_counter,
        )

    async def setting_time_limit(
        self,
        ip: str,
        name: str,
        attempt_counter: AttemptCounterDTO,
    ) -> None:
        if attempt_counter.ip_counter == 1:
            await self.rate_limiter.setting_a_time_limit_user_ip(
                ip=ip,
                seconds=self.time_limit,
            )
        if attempt_counter.name_counter == 1:
            await self.rate_limiter.setting_a_time_limit_user_name(
                name=name,
                seconds=self.time_limit,
            )
