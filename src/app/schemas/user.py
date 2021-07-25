from typing import List, Optional
from pydantic import BaseModel

from .squad import Squad


class UserBase(BaseModel):
    email: str
    username: str
    team_name: str


class UserCreate(UserBase):
    password: str


class UserEdit(BaseModel):
    username: Optional[str]
    team_name: Optional[str]
    avatar_path: Optional[str]
    squads: Optional[List[Squad]]


class UserPrivateEdit(BaseModel):
    password: str
    new_password: Optional[str]
    new_email: Optional[str]


class User(UserBase):
    avatar_path: str
    squads: List[Squad]

    class Config:
        orm_mode = True
