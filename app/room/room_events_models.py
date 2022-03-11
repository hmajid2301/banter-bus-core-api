from abc import ABC, abstractmethod
from typing import List, Union

from pydantic import BaseModel, validator

CREATE_ROOM = "CREATE_ROOM"
ROOM_CREATED = "ROOM_CREATED"
ERROR = "ERROR"
JOIN_ROOM = "JOIN_ROOM"
REJOIN_ROOM = "REJOIN_ROOM"
ROOM_JOINED = "ROOM_JOINED"
NEW_ROOM_JOINED = "NEW_ROOM_JOINED"
KICK_PLAYER = "KICK_PLAYER"
PLAYER_KICKED = "PLAYER_KICKED"
PLAYER_DISCONNECTED = "PLAYER_DISCONNECTED"
HOST_DISCONNECTED = "HOST_DISCONNECTED"
PERMANENTLY_DISCONNECT_PLAYER = "PERMANENTLY_DISCONNECT_PLAYER"
PERMANENTLY_DISCONNECTED_PLAYER = "PERMANENTLY_DISCONNECTED_PLAYER"
START_GAME = "START_GAME"
GAME_STARTED = "GAME_STARTED"


class EventModel(BaseModel, ABC):
    @property
    @abstractmethod
    def event_name(self) -> str:
        raise NotImplementedError


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
    avatar: Union[str, bytes]
    room_code: str

    @validator("avatar", pre=True)
    def base64_string_to_bytes(cls, value):
        if isinstance(value, str):
            return value.encode()
        return value

    @property
    def event_name(self):
        return JOIN_ROOM


class RejoinRoom(EventModel):
    player_id: str

    @property
    def event_name(self):
        return REJOIN_ROOM


class Player(BaseModel):
    nickname: str
    avatar: Union[str, bytes]

    @validator("avatar", pre=True)
    def base64_bytes_to_string(cls, value):
        if isinstance(value, bytes):
            return value.decode()
        return value


class RoomJoined(EventModel):
    host_player_nickname: str
    players: List[Player]

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


class PlayerDisconnected(EventModel):
    nickname: str
    avatar: Union[str, bytes]

    @validator("avatar", pre=True)
    def base64_bytes_to_string(cls, value):
        if isinstance(value, bytes):
            return value.decode()
        return value

    @property
    def event_name(self):
        return PLAYER_DISCONNECTED


class HostDisconnected(EventModel):
    new_host_nickname: str

    @property
    def event_name(self):
        return HOST_DISCONNECTED


class PermanentlyDisconnectPlayer(EventModel):
    nickname: str
    room_code: str

    @property
    def event_name(self):
        return PERMANENTLY_DISCONNECT_PLAYER


class PermanentlyDisconnectedPlayer(EventModel):
    nickname: str

    @property
    def event_name(self):
        return PERMANENTLY_DISCONNECTED_PLAYER


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


class Error(EventModel):
    code: str
    message: str

    @property
    def event_name(self):
        return ERROR
