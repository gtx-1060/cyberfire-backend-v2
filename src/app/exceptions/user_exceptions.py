from .base import MyException


class UserAlreadyExists(MyException):
    def __init__(self):
        super().__init__(400, "user with this data already exists")


class UserNotFound(MyException):
    def __init__(self):
        super().__init__(404, "user with this email not found")


class IncorrectUserDataException(MyException):
    def __init__(self, text):
        super().__init__(400, text)
