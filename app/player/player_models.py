from datetime import datetime

from pydantic.main import BaseModel


class NewPlayer(BaseModel):
    avatar: bytes
    nickname: str
    latest_sid: str


class Player(BaseModel):
    player_id: str
    avatar: bytes
    nickname: str
    disconnected_at: datetime | None = None
    latest_sid: str

    class Collection:
        name = "player"


class RoomPlayers(BaseModel):
    host_player_nickname: str
    player_id: str
    players: list[Player]
    room_code: str
