from ..models.roles import Roles
from pydantic import BaseModel


class TokenData:
    email: str
    role: Roles

    def __init__(self, email: str, role: Roles):
        self.email = email
        self.role = role


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
