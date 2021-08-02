from .base import MyException


class NotAllowedForTVT(MyException):
    def __init__(self):
        super().__init__(400, "this method not allowed for tvt-game tournaments")


class StageMustBeEmpty(MyException):
    def __init__(self, stage_id: int):
        super().__init__(400, f"stage (id {stage_id}) must have no matches for automatic start")