from datetime import datetime
from typing import List

from app.room.room_models import GameState, Room

rooms: List[Room] = [
    Room(
        **{
            "room_id": "4d18ac45-8034-4f8e-b636-cf730b17e51a",
            "game_name": "quibly",
            "room_code": "ABCDE",
            "players": [],
            "state": GameState.CREATED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    ),
    Room(
        **{
            "room_id": "a4ffd1c8-93c5-4f4c-8ace-71996edcbcb7",
            "game_name": "fibbing_it",
            "room_code": "ZXCVB",
            "players": [],
            "state": GameState.FINISHED,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    ),
]
