import abc
from datetime import datetime
from typing import List

from omnibus.database.repository import AbstractRepository
from pymongo.errors import DuplicateKeyError

from app.player.player_exceptions import PlayerExistsException, PlayerNotFound
from app.player.player_models import Player


class AbstractPlayerRepository(AbstractRepository[Player]):
    @abc.abstractmethod
    async def get_all_in_room(self, room_id: str) -> List[Player]:
        raise NotImplementedError

    @abc.abstractmethod
    async def remove_from_room(self, player: Player) -> Player:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_nickname(self, room_id: str, nickname: str) -> Player:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_disconnect(self) -> List[Player]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_sid(self, sid: str) -> Player:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_disconnected_at(self, player: Player) -> Player:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_sid(self, player: Player, sid: str) -> Player:
        raise NotImplementedError


class PlayerRepository(AbstractPlayerRepository):
    async def add(self, player: Player):
        try:
            await Player.insert(player)
        except DuplicateKeyError:
            raise PlayerExistsException(f"player {player.player_id=} already exists")

    async def get(self, id_: str) -> Player:
        player = await Player.find_one(Player.player_id == id_)
        if player is None:
            raise PlayerNotFound(f"player {id_=} not found")

        return player

    async def get_all_in_room(self, room_id: str) -> List[Player]:
        players = await Player.find(Player.room_id == room_id).to_list()
        return players

    async def get_by_nickname(self, room_id: str, nickname: str) -> Player:
        player = await Player.find_one(Player.nickname == nickname, Player.room_id == room_id)
        if player is None:
            raise PlayerNotFound(f"player {nickname=} and {room_id=} not found")
        return player

    async def get_disconnect(self) -> List[Player]:
        players = await Player.find(Player.disconnected_at != None).to_list()  # noqa
        return players

    async def get_by_sid(self, sid: str) -> Player:
        player = await Player.find_one(Player.latest_sid == sid)
        if player is None:
            raise PlayerNotFound(f"player {sid=} not found")
        return player

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def remove_from_room(self, player: Player) -> Player:
        player.room_id = None
        await player.save()
        return player

    async def update_disconnected_at(self, player: Player) -> Player:
        player.disconnected_at = datetime.now()
        await player.save()
        return player

    async def update_sid(self, player: Player, sid: str) -> Player:
        player.latest_sid = sid
        await player.save()
        return player
