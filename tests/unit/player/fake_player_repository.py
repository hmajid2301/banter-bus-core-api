from typing import List

from app.player.player_exceptions import PlayerExistsException
from app.player.player_models import Player
from app.player.player_repository import AbstractPlayerRepository


class FakePlayerRepository(AbstractPlayerRepository):
    def __init__(self, players: List[Player]):
        self.player = players

    async def add(self, new_player: Player):
        for player in self.player:
            if player.player_id == new_player.player_id:
                raise PlayerExistsException("player already exists")
        else:
            self.player.append(new_player)

    async def get(self, id_: str) -> Player:
        return await super().get(id_)

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def get_all_in_room(self, room_id: str) -> List[Player]:
        players = []
        for player in self.player:
            if player.room_id == room_id:
                players.append(player)

        return players
