from datetime import datetime

from app.room.room_models import Room, RoomState

rooms: list[Room] = [
    Room(
        room_id="4d18ac45-8034-4f8e-b636-cf730b17e51a",
        game_name="quibly",
        host=None,
        state=RoomState.CREATED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        player_count=0,
    ),
    Room(
        room_id="5a18ac45-9876-4f8e-b636-cf730b17e59l",
        game_name="fibbing_it",
        host="52dcb730-93ad-4364-917a-8760ee50d0f5",
        state=RoomState.CREATED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        player_count=4,
    ),
    Room(
        room_id="2257856e-bf37-4cc4-8551-0b1ccdc38c60",
        game_name="fibbing_it",
        host="8cdc1984-e832-48c7-9d89-1d724665bef1",
        state=RoomState.PLAYING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        player_count=4,
    ),
    Room(
        room_id="a4ffd1c8-93c5-4f4c-8ace-71996edcbcb7",
        game_name="fibbing_it",
        host="",
        state=RoomState.FINISHED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        player_count=2,
    ),
]
