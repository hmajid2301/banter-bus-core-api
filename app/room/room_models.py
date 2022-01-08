from datetime import datetime
from enum import Enum
from typing import List, Optional

from beanie import Document, Indexed
from pydantic.main import BaseModel


class RoomCodes(BaseModel):
    room_codes: List[str]


class RoomState(Enum):
    CREATED = "CREATED"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    ABANDONED = "ABANDONED"


class Room(Document):
    room_id: Indexed(str, unique=True)  # type: ignore
    game_name: Optional[str] = None
    room_code: str
    host: Optional[str] = None
    state: RoomState
    created_at: datetime
    updated_at: datetime

    class Collection:
        name = "room"
