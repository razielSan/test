from typing import List, Sequence, Any

from fastapi import Request

from app.my_project.backend.presentation.url import ApiMainUrl
from dto.exceptions import ValidationErrorItem


def format_validation_errors(
    exc: Sequence[Any],
) -> List[ValidationErrorItem]:
    errors: List[ValidationErrorItem] = [
        {
            "message": str(err["msg"]),
            "location": ".".join(map(str, err["loc"])),
        }
        for err in exc
    ]
    return errors


def is_api_request(request: Request) -> bool:
    if request.url.path.startswith(ApiMainUrl.PREFIX):
        return True
    return False
