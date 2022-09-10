from app.core.exceptions import ExistsException, NotFoundException


class PlayerExistsException(ExistsException):
    pass


class PlayerNotFound(NotFoundException):
    pass


class PlayerHasNoRoomError(NotFoundException):
    pass


class PlayerNotInRoom(NotFoundException):
    pass


class PlayerAlreadyDisconnected(Exception):
    pass


class PlayerNotHostError(NotFoundException):
    def __init__(self, msg: str, player_id: str, host_player_id) -> None:
        self.msg = msg
        self.player_id = player_id
        self.host_player_id = host_player_id


class NicknameExistsException(ExistsException):
    def __init__(self, msg: str, nickname: str) -> None:
        self.msg = msg
        self.nickname = nickname
