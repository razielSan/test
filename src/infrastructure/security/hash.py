from argon2.exceptions import VerifyMismatchError

from domain.exceptions import IncorrectPassword
from infrastructure.extensions import ph


class ArgonHasher:
    def hash(self, password: str) -> str:
        return ph.hash(password=password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            verify = ph.verify(password=password, hash=password_hash)
        except VerifyMismatchError as exc:
            raise IncorrectPassword() from exc
        else:
            return verify
