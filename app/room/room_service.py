from datetime import datetime
from uuid import uuid4

from app.room.room_models import Room, RoomState
from app.room.room_repository import AbstractRoomRepository


class RoomService:
    def __init__(self, room_repository: AbstractRoomRepository) -> None:
        self.room_repository = room_repository

    async def create(self) -> Room:
        room_id = uuid4()

        room = Room(
            room_id=str(room_id),
            state=RoomState.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await self.room_repository.add(room)
        return room

    async def get(self, room_id: str) -> Room:
        room = await self.room_repository.get(id_=room_id)
        return room

    async def update_host(self, room: Room, player_id: str) -> Room:
        room = await self.room_repository.update_host(room=room, player_id=player_id)
        return room

    async def update_game_state(self, room: Room, new_room_state: RoomState) -> Room:
        room = await self.room_repository.update_game_state(room=room, new_room_state=new_room_state)
        return room

    async def update_player_count(self, room: Room, increment: bool):
        new_count = room.player_count
        if increment:
            new_count += 1
        else:
            new_count -= 1

        await self.room_repository.update_player_count(room, new_count)
