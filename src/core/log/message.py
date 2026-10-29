from enum import Enum


class UserLog(str, Enum):
    CREATED = "Created user username='%s'"
    AUTHENTICATED = "Authenticated user username='%s'"
    UPDATED = "Updated user username='%s'"
    DELETED = "Deleted user user_id='%s'"
