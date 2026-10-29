from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenName(str, Enum):  # cookie names, not secret application data.
    ACCESS_TOKEN = "access_token"  # nosec B105
    REFRESH_TOKEN = "refresh_token"  # nosec B105


class ResponseMessageUser:
    LOGOUT_SUCCESS = {"message": "Logouted Successfully"}
    NOT_AUTHTENTICATE = {"message": "Not Authenticate"}
    UPDATE_ACCESS_TOKEN_SUCCESS = {
        "message": "Updated Access Token Successfully",
    }
