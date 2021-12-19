from datetime import datetime
from enum import Enum
from typing import List

from beanie import Document, Indexed
from pydantic.main import BaseModel


class RoomCodes(BaseModel):
    room_codes: List[str]


class GameState(Enum):
    CREATED = "CREATED"
    JOINING = "JOINING"
    PLAYING = "PLAYING"
    FINISHED = "FINISHED"
    ABANDONED = "ABANDONED"


class Room(Document):
    room_id = Indexed(str, unique=True)  # type: ignore
    game_name: str
    room_code: str
    players: List[str]
    state: GameState
    created_at: datetime
    updated_at: datetime

    class Collection:
        name = "room"
