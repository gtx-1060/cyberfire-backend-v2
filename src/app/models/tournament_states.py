import enum


class States(enum):
    WAITING_FOR_START = 'waiting',
    REGISTRATION = 'registration',
    IS_ON = 'is-on',
    FINISHED = 'finished'
