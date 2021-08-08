from enum import Enum


class States(Enum):
    PAUSED = 'paused'
    REGISTRATION = 'registration'
    IS_ON = 'is-on'
    FINISHED = 'finished'
