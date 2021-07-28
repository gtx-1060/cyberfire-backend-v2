from fastapi import HTTPException


class MyException(HTTPException):
    def __init__(self, status_code: int, exception: str):
        self.status_code = status_code
        self.detail = {'exception': exception, 'exception_type': type(self).__name__}
        print(str(self.detail))


class ItemNotFound(MyException):
    def __init__(self):
        super().__init__(404, "item not found")


class WrongFilePath(MyException):
    def __init__(self):
        super().__init__(400, "wrong wile path")


class FileSaveException(MyException):
    def __init__(self):
        super().__init__(400, "problem with saving file occurred")


class FileRemoveException(MyException):
    def __init__(self):
        super().__init__(400, "problem with removing file occurred")