from app.clients.management_api.exceptions import UnexpectedResponse
from app.core.exceptions import ExistsException, NotFoundException
from app.room.room_models import RoomState


class RoomExistsException(ExistsException):
    pass


class GameNotFound(NotFoundException):
    def __init__(self, e: UnexpectedResponse, message: str | None = None) -> None:
        self.e = e
        self.message = message


class GameNotEnabled(Exception):
    pass


class RoomNotFound(NotFoundException):
    def __init__(self, msg: str, id_: str) -> None:
        self.msg = msg
        self.id = id_


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


class PlayerCountError(Exception):
    def __init__(self, msg: str, room_id: str, game_name: str, room_player_count: int, game_players: int) -> None:
        self.msg = msg
        self.room_id = room_id
        self.game_name = game_name
        self.room_player_count = room_player_count
        self.game_players = game_players


class TooManyPlayersInRoomError(PlayerCountError):
    def __init__(
        self, msg: str, room_id: str, game_name: str, room_player_count: int, game_maximum_players: int
    ) -> None:
        super().__init__(msg, room_id, game_name, room_player_count, game_players=game_maximum_players)


class TooFewPlayersInRoomError(PlayerCountError):
    def __init__(
        self, msg: str, room_id: str, game_name: str, room_player_count: int, game_minimum_players: int
    ) -> None:
        super().__init__(msg, room_id, game_name, room_player_count, game_players=game_minimum_players)


class NicknameExistsException(ExistsException):
    def __init__(self, msg: str, nickname: str) -> None:
        self.msg = msg
        self.nickname = nickname
