from .base import MyException


class NotAllowedForTVT(MyException):
    def __init__(self):
        super().__init__(400, "this method not allowed for tvt-game tournaments")


class StageMustBeEmpty(MyException):
    def __init__(self, stage_id: int):
        super().__init__(400, f"stage (id {stage_id}) must have no matches for automatic start")


class TournamentAlreadyFinished(MyException):
    def __init__(self, t_id: int):
        super().__init__(400, f"tournament {t_id} already finished, but starting next stage task was executed")


class StatsOfNotParticipatedTeam(MyException):
    def __init__(self):
        super().__init__(400, "all stats haven't upload because of wrong 'team' field")


class MaxSquadsCount(MyException):
    def __init__(self):
        super().__init__(400, "the maximum number of players registered in the tournament")


class UserAlreadyRegistered(MyException):
    def __init__(self, email: str):
        super().__init__(400, f"{email} user already registered in tournament")


class UserNotRegistered(MyException):
    def __init__(self, email: str):
        super().__init__(400, f"{email} user wasn't registered in tournament")


class WrongTournamentState(MyException):
    def __init__(self):
        super().__init__(400, "you couldn't register/unregister to tournament now")


class WrongTournamentDates(MyException):
    def __init__(self):
        super().__init__(400, "date of tournament calculated from stage dates are wrong")


class NotEnoughPlayersInSquad(MyException):
    def __init__(self):
        super().__init__(400, "not enough players in user's squad")
