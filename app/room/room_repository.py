import abc
from datetime import datetime
from typing import Any

from omnibus.database.repository import AbstractRepository
from pymongo.errors import DuplicateKeyError

from app.player.player_exceptions import PlayerNotFound
from app.player.player_models import Player
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
        except DuplicateKeyError as e:
            raise RoomExistsException(f"room {room.room_id=} already exists") from e

    async def add_player(self, room: Room, player: Player):
        room.players.append(player)
        await room.save()

    async def get(self, id_: str) -> Room:
        room = await Room.find_one(Room.room_id == id_)
        if room is None:
            raise RoomNotFound(msg="room not found using id", id_=id_)
        return room

    async def get_room_by_player_id(self, player_id: str) -> Room:
        room = await Room.find_one({"players.player_id": player_id})
        if room is None:
            raise RoomNotFound(msg="room not found using player id", id_=player_id)
        return room

    async def get_player(self, player_id: str) -> Player:
        if aggregate := await Room.aggregate(
            [{"$unwind": "$players"}, {"$match": {"players.player_id": player_id}}]
        ).to_list():
            player = aggregate[0]["players"]
            return Player(**player)
        else:
            raise PlayerNotFound("player not found")

    async def get_all_players(self, room_id: str) -> list[Player]:
        room = await self.get(id_=room_id)
        return room.players

    async def get_player_by_sid(self, sid: str) -> Player:
        return await self._get_player_by_field(field_name="latest_sid", field_value=sid, extra_matches={})

    async def get_player_by_nickname(self, room_id: str, nickname: str) -> Player:
        return await self._get_player_by_field(
            field_name="nickname", field_value=nickname, extra_matches={"room_id": room_id}
        )

    async def _get_player_by_field(self, field_name: str, field_value: Any, extra_matches: dict[str, str]) -> Player:
        if aggregate := await Room.aggregate(
            [{"$unwind": "$players"}, {"$match": {f"players.{field_name}": field_value, **extra_matches}}]
        ).to_list():
            player = aggregate[0]["players"]
            return Player(**player)
        else:
            raise PlayerNotFound("player not found")

    async def remove_player(self, room: Room, nickname: str) -> Player:
        player = await self.get_player_by_nickname(room_id=room.room_id, nickname=nickname)
        await room.update({"$pull": {"players": {"nickname": nickname}}})
        return player

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def update_host(self, room: Room, player_id: str):
        room.host = player_id
        await room.save()

    async def update_game_state(self, room: Room, new_room_state: RoomState):
        room.state = new_room_state
        await room.save()

    async def update_player_disconnected_at(self, sid: str, disconnected_at: datetime | None = None):
        await Room.find_one({"players.latest_sid": sid}).update(
            {"$set": {"players.$.disconnected_at": disconnected_at}}
        )

    async def update_sid(self, player_id: str, sid: str):
        await Room.find_one({"players.player_id": player_id}).update({"$set": {"players.$.latest_sid": sid}})
