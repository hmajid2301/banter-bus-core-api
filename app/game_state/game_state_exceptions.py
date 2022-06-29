from datetime import datetime

from app.core.exceptions import ExistsException, NotFoundException


class GameStateExistsException(ExistsException):
    pass


class GameStateNotFound(NotFoundException):
    def __init__(self, msg: str, room_identifier: str) -> None:
        self.msg = msg
        self.room_identifier = room_identifier


class NoStateFound(NotFoundException):
    pass


class GameStateAlreadyPaused(Exception):
    pass


class GameStateNotPaused(Exception):
    pass


class GameIsPaused(Exception):
    pass


class InvalidGameAction(Exception):
    pass


class GameStateIsNoneError(Exception):
    pass


class InvalidGameState(Exception):
    pass


class ActionTimedOut(Exception):
    def __init__(self, msg: str, now: datetime, completed_by: datetime) -> None:
        self.msg = msg
        self.now = now
        self.completed_by = completed_by
