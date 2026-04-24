from typing import Generic, TypeVar

T = TypeVar("T")

class JsonReturn(Generic[T]):
    def __init__(self, status_code: int, message: str, data: T):
        self.code = status_code
        self.message = message
        self.data = data