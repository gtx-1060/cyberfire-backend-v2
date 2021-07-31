from .base import MyException


class FieldCouldntBeEdited(MyException):
    def __init__(self, field: str, reason: str):
        super().__init__(400, f"field '{field}' couldn't be edited because of {reason}")
