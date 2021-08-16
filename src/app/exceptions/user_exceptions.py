from .base import MyException


class UserAlreadyExists(MyException):
    def __init__(self):
        super().__init__(400, "Пользователь с таким же именем команды или почтой существует")


class UserNotFound(MyException):
    def __init__(self):
        super().__init__(404, "Искомого пользователя не существует")
