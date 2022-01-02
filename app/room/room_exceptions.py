from typing import Optional

from app.clients.management_api.exceptions import UnexpectedResponse
from app.core.exceptions import ExistsException, NotFoundException


class RoomExistsException(ExistsException):
    pass


class GameNotFound(NotFoundException):
    def __init__(self, e: UnexpectedResponse, message: Optional[str] = None) -> None:
        self.e = e
        self.message = message


class GameNotEnabled(Exception):
    pass


class RoomNotFound(NotFoundException):
    pass


class NicknameExistsException(ExistsException):
    def __init__(self, msg: str, nickname: str) -> None:
        self.msg = msg
        self.nickname = nickname
