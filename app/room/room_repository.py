import abc
from typing import List

from beanie.operators import NotIn
from pymongo.errors import DuplicateKeyError

from app.core.repository import AbstractRepository
from app.room.room_exceptions import RoomExistsException
from app.room.room_models import GameState, Room, RoomCodes


class AbstractRoomRepository(AbstractRepository[Room]):
    @abc.abstractmethod
    async def get_all_room_codes(self) -> List[str]:
        raise NotImplementedError


class RoomRepository(AbstractRoomRepository):
    async def add(self, room: Room):
        try:
            await Room.insert(room)
        except DuplicateKeyError:
            raise RoomExistsException(f"question {room.room_id=} already exists")

    async def get_all_room_codes(self) -> List[str]:
        rooms_code_aggregate: List[RoomCodes] = (
            await Room.find(NotIn(Room.state, [GameState.ABANDONED, GameState.FINISHED]))
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

    async def get(self, id_: str) -> Room:
        return await super().get(id_)

    async def remove(self, id_: str):
        return await super().remove(id_)
