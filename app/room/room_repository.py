import abc

from omnibus.database.repository import AbstractRepository
from pymongo.errors import DuplicateKeyError

from app.room.room_exceptions import RoomExistsException, RoomNotFound
from app.room.room_models import Room, RoomState


class AbstractRoomRepository(AbstractRepository[Room]):
    @abc.abstractmethod
    async def update_host(self, room: Room, player_id: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def update_game_state(self, room: Room, new_room_state: RoomState):
        raise NotImplementedError


class RoomRepository(AbstractRoomRepository):
    async def add(self, room: Room):
        try:
            await Room.insert(room)
        except DuplicateKeyError:
            raise RoomExistsException(f"player {room.room_id=} already exists")

    async def get(self, id_: str) -> Room:
        room = await Room.find_one(Room.room_id == id_)
        if room is None:
            raise RoomNotFound(msg="room not found", room_idenitifer=id_)
        return room

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def update_host(self, room: Room, player_id: str):
        room.host = player_id
        await room.save()

    async def update_game_state(self, room: Room, new_room_state: RoomState):
        room.state = new_room_state
        await room.save()
