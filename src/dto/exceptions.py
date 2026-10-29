from typing import List, Union, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict

from core.constants.error import ErrorCode


class ValidationErrorItem(TypedDict):
    message: str
    location: str


class ErrorResponseDTO(BaseModel):
    code: str
    message: Union[List[ValidationErrorItem], str]

    model_config = ConfigDict(extra="forbid")


class ValidationErrorDTO:
    def __init__(
        self,
        message: Optional[List[ValidationErrorItem]] = None,
    ) -> None:
        self.message = (
            [
                {
                    "message": "Default message",
                    "location": "default location",
                },
            ]
            if message is None
            else message
        )
        self.code = ErrorCode.VALIDATION_ERROR.value
        self.status_code = 400
        self.content = {
            "code": self.code,
            "message": self.message,
        }


class UnknownExceptionDTO:
    def __init__(self) -> None:
        self.status_code = 500
        self.content = {
            "code": "UNKNOWN EXCEPTION",
            "message": "An unknown error has occurred try making the request again",
        }


class AppExceptionDTO:
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.content = {
            "code": code,
            "message": message,
        }


class NotFoundPageDTO:
    def __init__(self) -> None:
        self.status_code = 404
        self.content = {
            "code": "NOT FOUND",
            "message": "page not found",
        }
