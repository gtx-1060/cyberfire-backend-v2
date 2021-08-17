from typing import List, Optional
from pydantic import BaseModel, validator

from .squad import Squad
from ..models.roles import Roles
from src.app.exceptions.formatter_exceptions import *


def validate_email(v):
    if ('@' not in v) or len(v) > 50 or len(v) < 4:
        raise IncorrectUserDataException('Некорректная почта')
    return v.lower()


def validate_username(v):
    if len(v) < 3 or len(v) > 20:
        raise IncorrectUserDataException('Имя пользователя должно быть длиннее 2 символов и короче 20')
    if ' ' in v:
        raise IncorrectUserDataException('Имя пользователя не должно содержать пробелы')
    return v.lower()


def validate_team(v):
    if len(v) < 3 or len(v) > 20:
        raise IncorrectUserDataException('Название команды должно быть длиннее 2 символов и короче 20')
    return v.lower()


def validate_password(v):
    if len(v) < 5:
        raise IncorrectUserDataException('Пароль должен быть не короче 5 символов')
    if ' ' in v:
        raise IncorrectUserDataException('Пароль не должен содержать пробелы')
    return v.lower()


class UserBase(BaseModel):
    email: str
    username: str
    team_name: str


class UserCreate(UserBase):
    password: str

    @validator('email')
    def base_mail_validator(cls, v):
        return validate_email(v)

    @validator('username')
    def base_username_validator(cls, v):
        return validate_username(v)

    @validator('team_name')
    def base_team_validator(cls, v):
        return validate_team(v)

    @validator('password')
    def base_password_validator(cls, v):
        return validate_password(v)


class UserEdit(BaseModel):
    username: Optional[str]
    team_name: Optional[str]
    avatar_path: Optional[str]
    squads: Optional[List[Squad]]

    @validator('username')
    def base_username_validator(cls, v):
        if v is None:
            return v
        return validate_username(v)

    @validator('team_name')
    def base_team_validator(cls, v):
        if v is None:
            return v
        return validate_team(v)


class UserPrivateEdit(BaseModel):
    old_password: str
    new_password: Optional[str]
    new_email: Optional[str]

    @validator('new_password')
    def base_password_validator(cls, v):
        if v is None:
            return v
        return validate_password(v)

    @validator('new_email')
    def base_mail_validator(cls, v):
        if v is None:
            return v
        return validate_email(v)


class User(UserBase):
    avatar_path: str
    role: Roles
    squads: List[Squad]

    class Config:
        orm_mode = True
