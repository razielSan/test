from dataclasses import dataclass


@dataclass
class UserDOMAIN:
    id: int
    username: str
    password_hash: str
    is_active: bool
