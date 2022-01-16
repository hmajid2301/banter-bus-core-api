from typing import List

from pydantic import BaseModel, validator

CREATE_ROOM = "CREATE_ROOM"
ROOM_CREATED = "ROOM_CREATED"
ERROR = "ERROR"
JOIN_ROOM = "JOIN_ROOM"
REJOIN_ROOM = "REJOIN_ROOM"
ROOM_JOINED = "ROOM_JOINED"


class CreateRoom(BaseModel):
    pass


class RoomCreated(BaseModel):
    room_code: str


class JoinRoom(BaseModel):
    avatar: bytes
    nickname: str
    room_code: str

    @validator("avatar", pre=True)
    def base64_string_to_bytes(cls, value):
        if isinstance(value, str):
            return value.encode()
        return value


class RejoinRoom(BaseModel):
    player_id: str


class Player(BaseModel):
    avatar: str
    nickname: str

    @validator("avatar", pre=True)
    def base64_bytes_to_string(cls, value):
        if isinstance(value, bytes):
            return value.decode()
        return value


class RoomJoined(BaseModel):
    host_player_nickname: str
    player_id: str
    players: List[Player]


class Error(BaseModel):
    code: str
    message: str
