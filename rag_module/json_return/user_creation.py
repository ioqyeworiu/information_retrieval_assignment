from json_return import JsonReturn
from dto.user_dto import UserDTO

class UserCreationReturn(JsonReturn[UserDTO]):
    def __init__(self, status_code: int, message: str, data: UserDTO):
        super().__init__(status_code, message, data)
        