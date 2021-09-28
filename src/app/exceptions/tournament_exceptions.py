from datetime import datetime

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


class StageAlreadyFinished(MyException):
    def __init__(self, s_id: int):
        super().__init__(400, f"stage {s_id} already finished, but starting next stage task was executed")


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
        super().__init__(425, "something wrong with tournament state")


class WrongTournamentDates(MyException):
    def __init__(self, date: datetime):
        super().__init__(400, f"date of tournament ({date}) calculated from stage dates are wrong")


class NotEnoughPlayersInSquad(MyException):
    def __init__(self):
        super().__init__(400, "not enough players in user's squad")


class AllStagesMustBeFinished(MyException):
    def __init__(self):
        super().__init__(400, "all stages must be finished")


class MatchMustHaveOnlyTwoStats(MyException):
    def __init__(self):
        super().__init__(400, "There should be two statistics in a match - the player and his opponent.")


class UserCantConnectHere(MyException):
    def __init__(self):
        super().__init__(403, "User cant connect here")


class MapChoiceDataNotFound(MyException):
    def __init__(self):
        super().__init__(404, "Map choice data not found")


class ResultProofLoadError(MyException):
    def __init__(self, s):
        super().__init__(404, s)


class TournamentInternalStateException(MyException):
    def __init__(self):
        super().__init__(400, 'wrong tournament state')


class AllStatsMustBeVerified(MyException):
    def __init__(self):
        super().__init__(400, 'all statistics must be confirmed')


class GameNotFoundInTvtPool(MyException):
    def __init__(self):
        super().__init__(400, 'game not found in tvt pool')