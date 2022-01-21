from typing import List

from app.player.player_exceptions import PlayerExistsException, PlayerNotFound
from app.player.player_models import Player
from app.player.player_repository import AbstractPlayerRepository


class FakePlayerRepository(AbstractPlayerRepository):
    def __init__(self, players: List[Player]):
        self.players = players

    async def add(self, new_player: Player):
        for player in self.players:
            if player.player_id == new_player.player_id:
                raise PlayerExistsException("player already exists")
        else:
            self.players.append(new_player)

    async def get(self, id_: str) -> Player:
        for player in self.players:
            if player.player_id == id_:
                return player

        raise PlayerNotFound("player not found")

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def get_all_in_room(self, room_id: str) -> List[Player]:
        players = []
        for player in self.players:
            if player.room_id == room_id:
                players.append(player)

        return players

    async def remove_room(self, player: Player) -> Player:
        player.room_id = None
        return player

    async def get_by_nickname(self, room_id: str, nickname: str) -> Player:
        for player in self.players:
            if player.room_id == room_id and player.nickname == nickname:
                return player

        raise PlayerNotFound("player not found")
