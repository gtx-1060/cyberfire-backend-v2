from enum import Enum


class TournamentStates(Enum):
    PAUSED = 'paused'
    REGISTRATION = 'registration'
    IS_ON = 'is-on'
    FINISHED = 'finished'


class StageStates(Enum):
    WAITING = 'waiting'
    IS_ON = 'is-on'
    FINISHED = 'finished'
