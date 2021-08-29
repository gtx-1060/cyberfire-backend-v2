from datetime import datetime
from os.path import join
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Request
from uuid import uuid1
from pathlib import Path
from os import remove

from src.app.config import ABSOLUTE_PATH, ALGORITHM, SECRET_KEY
from src.app.exceptions.base import WrongFilePath, FileSaveException, FileRemoveException
from src.app.middleware.log_middleware import error_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_str_hash(string: str) -> str:
    return pwd_context.hash(string)


def verify_hashed(string_hash: str, string: str) -> bool:
    return pwd_context.verify(string, string_hash)


def get_db(request: Request):
    return request.state.db


def generate_jwt(payload: dict, expires_delta) -> str:
    expire = datetime.utcnow() + expires_delta
    payload['exp'] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def data_from_jwt(token: str) -> Optional[dict]:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data
    except JWTError:
        return None


def save_image(path: str, content) -> str:
    if "static" not in path:
        raise WrongFilePath()
    full_path = join(path, f"{uuid1()}.jpg")
    try:
        with open(full_path, 'wb') as f:
            f.write(content)
            f.close()
        return full_path[full_path.find('static')::].replace("\\", "/")
    except Exception as e:
        error_logger.error(str(e))
        raise FileSaveException(str(e))


def delete_image_by_web_path(web_path: str):
    if 'default' in web_path:
        return
    full_path = join(Path(ABSOLUTE_PATH), web_path)
    try:
        remove(full_path)
    except Exception as e:
        error_logger.error(str(e))
        raise FileRemoveException(str(e))
