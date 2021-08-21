from .base import MyException


class FieldCouldntBeEdited(MyException):
    def __init__(self, field: str, reason: str):
        super().__init__(400, f"field '{field}' couldn't be edited because of {reason}")


class SameItemAlreadyExists(MyException):
    def __init__(self, item_id=''):
        super().__init__(400, f"Same item {item_id} already exists in db table")
