from datetime import datetime

from beanie import Document, Indexed
from pydantic.main import BaseModel


class NewPlayer(BaseModel):
    avatar: bytes
    nickname: str
    latest_sid: str


class Player(Document):
    player_id: Indexed(str, unique=True)  # type: ignore
    avatar: bytes
    nickname: str
    room_id: str | None = None
    disconnected_at: datetime | None = None
    latest_sid: str

    class Collection:
        name = "player"


class RoomPlayers(BaseModel):
    host_player_nickname: str
    player_id: str
    players: list[Player]
    room_code: str
