from datetime import datetime
from typing import Union

from pydantic import BaseModel, Field, ConfigDict, field_validator

from core.utils.validation import validate_password_strength


class CreateUserDTO(BaseModel):
    password: str = Field(min_length=12)
    username: str = Field(min_length=3, max_length=30)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value=value)

    model_config = ConfigDict(extra="forbid")


class AuthenticateUserDTO(BaseModel):
    password: str
    username: str

    model_config = ConfigDict(extra="forbid")


class UpdateUserPasswordDTO(BaseModel):
    password: str
    new_password: str = Field(min_length=12)

    model_config = ConfigDict(extra="forbid")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value=value)


class UpdateUserNameDTO(BaseModel):
    password: str
    username: str = Field(min_length=3, max_length=30)

    model_config = ConfigDict(extra="forbid")


class UserDTO(BaseModel):
    id: int
    username: str
    is_active: bool

    model_config = ConfigDict(extra="forbid")


class TokenDTO(BaseModel):
    sub: str
    exp: Union[datetime, int]
    type_token: str

    model_config = ConfigDict(extra="forbid")


class AttemptCounterDTO(BaseModel):
    ip_counter: int
    name_counter: int

    model_config = ConfigDict(extra="forbid")
