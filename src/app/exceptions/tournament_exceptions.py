from .base import MyException


class NotAllowedForTVT(MyException):
    def __init__(self):
        super().__init__(400, "this method not allowed for tvt-game tournaments")