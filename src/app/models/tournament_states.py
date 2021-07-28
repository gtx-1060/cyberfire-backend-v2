from enum import Enum


class States(Enum):
    WAITING_FOR_START = 'waiting',
    REGISTRATION = 'registration',
    IS_ON = 'is-on',
    FINISHED = 'finished'
