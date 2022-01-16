import abc
from typing import List

from omnibus.database.repository import AbstractRepository
from pymongo.errors import DuplicateKeyError

from app.player.player_exceptions import PlayerExistsException, PlayerNotFound
from app.player.player_models import Player


class AbstractPlayerRepository(AbstractRepository[Player]):
    @abc.abstractmethod
    async def get_all_in_room(self, room_id: str) -> List[Player]:
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

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def get_all_in_room(self, room_id: str) -> List[Player]:
        players = await Player.find(Player.room_id == room_id).to_list()
        return players
