from typing import List

from app.room.room_exceptions import RoomExistsException, RoomNotFound
from app.room.room_models import Room, RoomState
from app.room.room_repository import AbstractRoomRepository


class FakeRoomRepository(AbstractRoomRepository):
    def __init__(self, rooms: List[Room]):
        self.rooms = rooms

    async def add(self, new_room: Room):
        for room in self.rooms:
            if room.room_id == new_room.room_id:
                raise RoomExistsException("room already exists")
        else:
            self.rooms.append(new_room)

    async def get(self, id_: str) -> Room:
        for room in self.rooms:
            if room.room_id == id_:
                return room
        raise RoomNotFound("room not found", room_idenitifer=id_)

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def update_host(self, room: Room, player_id: str):
        for r in self.rooms:
            if r.room_id == room.room_id:
                r.host = player_id

    async def update_game_state(self, room: Room, new_room_state: RoomState):
        for r in self.rooms:
            if r.room_id == room.room_id:
                r.state = new_room_state
