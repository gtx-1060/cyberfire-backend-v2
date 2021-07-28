from .base import MyException


class AuthenticationException(MyException):
    def __init__(self, name):
        super().__init__(401, name)


class WrongCredentialsException(MyException):
    def __init__(self):
        super().__init__(400, "Auth failed: wrong credentials")


class UserIsNotActiveException(MyException):
    def __init__(self):
        super().__init__(400, "Auth failed: user isn't active")


class NotEnoughPermissions(MyException):
    def __init__(self):
        super().__init__(403, "You must be admin for this")