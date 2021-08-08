from os.path import join
from passlib.context import CryptContext
from fastapi import Request
from uuid import uuid1
from pathlib import Path
from os import remove

from src.app.config import ABSOLUTE_PATH
from src.app.exceptions.base import WrongFilePath, FileSaveException, FileRemoveException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return pwd_context.verify(password, password_hash)


def get_db(request: Request):
    return request.state.db


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
        print(e)
        raise FileSaveException()


def delete_image_by_web_path(web_path: str):
    if 'default' in web_path:
        return
    full_path = join(Path(ABSOLUTE_PATH), web_path.replace('/', r'\\'))
    try:
        remove(full_path)
    except Exception as e:
        print(e)
        raise FileRemoveException()
