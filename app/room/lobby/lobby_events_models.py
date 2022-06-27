from pydantic import BaseModel, validator

from app.event_models import EventModel

CREATE_ROOM = "CREATE_ROOM"
ROOM_CREATED = "ROOM_CREATED"
JOIN_ROOM = "JOIN_ROOM"
REJOIN_ROOM = "REJOIN_ROOM"
ROOM_JOINED = "ROOM_JOINED"
NEW_ROOM_JOINED = "NEW_ROOM_JOINED"
KICK_PLAYER = "KICK_PLAYER"
PLAYER_KICKED = "PLAYER_KICKED"
START_GAME = "START_GAME"
GAME_STARTED = "GAME_STARTED"


class CreateRoom(EventModel):
    @property
    def event_name(self):
        return CREATE_ROOM


class RoomCreated(EventModel):
    room_code: str

    @property
    def event_name(self):
        return ROOM_CREATED


class JoinRoom(EventModel):
    nickname: str
    avatar: str | bytes
    room_code: str

    @validator("avatar", pre=True)
    def base64_string_to_bytes(cls, value):
        if isinstance(value, str):
            return value.encode()
        return value

    @property
    def event_name(self):
        return JOIN_ROOM


class Player(BaseModel):
    nickname: str
    avatar: str | bytes

    @validator("avatar", pre=True)
    def base64_bytes_to_string(cls, value):
        if isinstance(value, bytes):
            return value.decode()
        return value


class RoomJoined(EventModel):
    host_player_nickname: str
    players: list[Player]

    @property
    def event_name(self):
        return ROOM_JOINED


class NewRoomJoined(EventModel):
    player_id: str

    @property
    def event_name(self):
        return NEW_ROOM_JOINED


class KickPlayer(EventModel):
    kick_player_nickname: str
    player_id: str
    room_code: str

    @property
    def event_name(self):
        return KICK_PLAYER


class PlayerKicked(EventModel):
    nickname: str

    @property
    def event_name(self):
        return PLAYER_KICKED


class StartGame(EventModel):
    player_id: str
    game_name: str
    room_code: str

    @property
    def event_name(self):
        return START_GAME


class GameStarted(EventModel):
    game_name: str

    @property
    def event_name(self):
        return GAME_STARTED
