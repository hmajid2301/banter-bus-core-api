from typing import Optional

from app.clients.management_api.exceptions import UnexpectedResponse
from app.core.exceptions import ExistsException, NotFoundException
from app.room.room_models import RoomState


class RoomExistsException(ExistsException):
    pass


class GameNotFound(NotFoundException):
    def __init__(self, e: UnexpectedResponse, message: Optional[str] = None) -> None:
        self.e = e
        self.message = message


class GameNotEnabled(Exception):
    pass


class RoomNotFound(NotFoundException):
    def __init__(self, msg: str, room_idenitifer: str) -> None:
        self.msg = msg
        self.room_idenitifer = room_idenitifer


class RoomInInvalidState(Exception):
    def __init__(self, msg: str, room_state: RoomState) -> None:
        self.msg = msg
        self.room_state = room_state


class RoomNotJoinableError(Exception):
    def __init__(self, msg: str, room_id: str, room_state: RoomState) -> None:
        self.msg = msg
        self.room_id = room_id
        self.room_state = room_state


class RoomHasNoHostError(Exception):
    def __init__(self, msg: str, room_id: str) -> None:
        self.msg = msg
        self.room_id = room_id


class NicknameExistsException(ExistsException):
    def __init__(self, msg: str, nickname: str) -> None:
        self.msg = msg
        self.nickname = nickname
