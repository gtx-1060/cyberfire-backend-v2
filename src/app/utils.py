from passlib.context import CryptContext
from fastapi import Request

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return pwd_context.verify(password, password_hash)


def get_db(request: Request):
    return request.state.db
