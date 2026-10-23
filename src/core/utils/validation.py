from core.constants.error import LetterNotFoundError, DigitNotFoundError


def validate_password_strength(value: str) -> str:
    if not any(v.isalpha() for v in value):
        raise ValueError(LetterNotFoundError.message)

    if not any(v.isdigit() for v in value):
        raise ValueError(DigitNotFoundError.message)

    return value
