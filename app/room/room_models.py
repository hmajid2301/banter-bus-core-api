from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Indexed


class RoomState(Enum):
    CREATED = "CREATED"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    ABANDONED = "ABANDONED"

    @property
    def is_room_joinable(self) -> bool:
        return self in [self.CREATED, self.PLAYING, self.PAUSED]


class Room(Document):
    room_id: Indexed(str, unique=True)  # type: ignore
    game_name: Optional[str] = None
    host: Optional[str] = None
    state: RoomState
    created_at: datetime
    updated_at: datetime

    class Collection:
        name = "room"
