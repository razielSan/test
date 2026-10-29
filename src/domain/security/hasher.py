from typing import Protocol


class PasswordHasherProtocol(Protocol):
    def hash(self, password: str) -> str:
        pass

    def verify(self, password_hash: str, password: str) -> bool:
        pass
