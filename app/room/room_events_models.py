from typing import List

from pydantic import BaseModel

CREATE_ROOM = "CREATE_ROOM"
ROOM_CREATED = "ROOM_CREATED"


class CreateRoom(BaseModel):
    game_name: str


class RoomCreated(BaseModel):
    room_code: str


class JoinRoom(BaseModel):
    avatar: bytes
    nickname: str
    room_code: str


class Player(BaseModel):
    avatar: bytes
    nickname: str


class RoomJoined(BaseModel):
    host_player_nickname: str
    players: List[Player]


class Error(BaseModel):
    code: str
    message: str
