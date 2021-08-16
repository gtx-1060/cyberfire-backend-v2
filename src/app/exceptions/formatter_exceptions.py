from src.app.exceptions.base import MyException


class IncorrectUserDataException(MyException):
    def __init__(self, text):
        super().__init__(400, text)
