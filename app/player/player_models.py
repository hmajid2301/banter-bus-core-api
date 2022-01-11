from typing import List

from beanie import Document, Indexed
from pydantic.main import BaseModel


class NewPlayer(BaseModel):
    avatar: bytes
    nickname: str


class Player(Document):
    player_id: Indexed(str, unique=True)  # type: ignore
    avatar: bytes
    nickname: str
    room_id: str

    class Collection:
        name = "player"


class RoomPlayers(BaseModel):
    host_player_nickname: str
    player_id: str
    players: List[Player]
