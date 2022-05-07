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


class GameStateAlreadyUnpaused(Exception):
    pass
