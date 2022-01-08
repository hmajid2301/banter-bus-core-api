import abc
from typing import List

from beanie.operators import NotIn
from omnibus.database.repository import AbstractRepository
from pymongo.errors import DuplicateKeyError

from app.room.room_exceptions import RoomExistsException, RoomNotFound
from app.room.room_models import Room, RoomCodes, RoomState


class AbstractRoomRepository(AbstractRepository[Room]):
    @abc.abstractmethod
    async def get_all_room_codes(self) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_room_code(self, room_code: str) -> Room:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_host(self, room: Room, player_id: str):
        raise NotImplementedError


class RoomRepository(AbstractRoomRepository):
    async def add(self, room: Room):
        try:
            await Room.insert(room)
        except DuplicateKeyError:
            raise RoomExistsException(f"player {room.room_id=} already exists")

    async def get(self, id_: str) -> Room:
        return await super().get(id_)

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def get_all_room_codes(self) -> List[str]:
        rooms_code_aggregate: List[RoomCodes] = (
            await Room.find(NotIn(Room.state, [RoomState.ABANDONED, RoomState.FINISHED]))
            .aggregate(
                [
                    {
                        "$group": {
                            "_id": "_id",
                            "room_codes": {"$addToSet": "$room_code"},
                        },
                    },
                    {"$unset": "_id"},
                ],
                projection_model=RoomCodes,
            )
            .to_list()
        )

        try:
            room_codes = rooms_code_aggregate[0].room_codes
        except IndexError:
            room_codes = []

        return room_codes

    async def get_by_room_code(self, room_code: str) -> Room:
        room = await Room.find_one(Room.room_code == room_code)
        if room is None:
            raise RoomNotFound(f"room with {room_code=} not found")
        return room

    async def update_host(self, room: Room, player_id: str):
        room.host = player_id
        await room.save()
