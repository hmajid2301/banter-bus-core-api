from typing import List

from app.room.room_exceptions import RoomExistsException
from app.room.room_models import Room
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
        return await super().get(id_)

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def get_all_room_codes(self) -> List[str]:
        room_codes: List[str] = []
        for room in self.rooms:
            room_codes.append(room.room_code)
        return room_codes
