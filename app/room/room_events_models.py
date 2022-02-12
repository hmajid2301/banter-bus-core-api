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


class CreateRoom(BaseModel):
    pass


class RoomCreated(BaseModel):
    room_code: str


class JoinRoom(BaseModel):
    nickname: str
    avatar: Union[str, bytes]
    room_code: str

    @validator("avatar", pre=True)
    def base64_string_to_bytes(cls, value):
        if isinstance(value, str):
            return value.encode()
        return value


class RejoinRoom(BaseModel):
    player_id: str


class Player(BaseModel):
    nickname: str
    avatar: Union[str, bytes]

    @validator("avatar", pre=True)
    def base64_bytes_to_string(cls, value):
        if isinstance(value, bytes):
            return value.decode()
        return value


class RoomJoined(BaseModel):
    host_player_nickname: str
    players: List[Player]


class NewRoomJoined(BaseModel):
    player_id: str


class KickPlayer(BaseModel):
    kick_player_nickname: str
    player_id: str
    room_code: str


class PlayerKicked(BaseModel):
    nickname: str


class PlayerDisconnected(BaseModel):
    nickname: str
    avatar: Union[str, bytes]

    @validator("avatar", pre=True)
    def base64_bytes_to_string(cls, value):
        if isinstance(value, bytes):
            return value.decode()
        return value


class HostDisconnected(BaseModel):
    new_host_nickname: str


class PermanentlyDisconnectPlayer(BaseModel):
    nickname: str
    room_code: str


class PermanentlyDisconnectedPlayer(BaseModel):
    nickname: str


class Error(BaseModel):
    code: str
    message: str
