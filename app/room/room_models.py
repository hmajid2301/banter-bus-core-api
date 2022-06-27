from __future__ import annotations

from datetime import datetime
from enum import Enum

from beanie import Document, Indexed


class RoomState(Enum):
    CREATED = "CREATED"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    ABANDONED = "ABANDONED"

    @property
    def is_room_joinable(self) -> bool:
        return self in [self.CREATED]

    @property
    def is_room_rejoinable(self) -> bool:
        return self in [self.CREATED, self.PLAYING, self.PAUSED]

    @property
    def is_room_rejoinable_and_started(self) -> bool:
        return self in [self.PLAYING, self.PAUSED]


class Room(Document):
    room_id: Indexed(str, unique=True)  # type: ignore
    game_name: str | None = None
    host: str | None = None
    state: RoomState
    player_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Collection:
        name = "room"
