from .base import MyException


class CannotScheduleTask(MyException):
    def __init__(self, task_id: str, original_error):
        super().__init__(500, f"Cannot schedule the task '{task_id}', OriginalError: '{type(original_error).__name__}'")


class CannotReScheduleTask(MyException):
    def __init__(self, task_id: str, original_error):
        super().__init__(500,
                         f"Cannot reschedule the task '{task_id}', OriginalError: '{type(original_error).__name__}'")


class CannotRemoveTask(MyException):
    def __init__(self, task_id: str, original_error):
        super().__init__(500,
                         f"Cannot remove the task '{task_id}', OriginalError: '{type(original_error).__name__}'")
