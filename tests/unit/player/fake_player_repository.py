from datetime import datetime
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

    async def get_disconnect(self) -> List[Player]:
        players = []
        for player in self.players:
            if player.disconnected_at:
                players.append(player)
        return players

    async def get_all_in_room(self, room_id: str) -> List[Player]:
        players = []
        for player in self.players:
            if player.room_id == room_id:
                players.append(player)

        return players

    async def get_by_nickname(self, room_id: str, nickname: str) -> Player:
        for player in self.players:
            if player.room_id == room_id and player.nickname == nickname:
                return player

        raise PlayerNotFound("player not found")

    async def get_by_sid(self, sid: str) -> Player:
        for player in self.players:
            if player.latest_sid == sid:
                return player

        raise PlayerNotFound("player not found")

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def remove_from_room(self, player: Player) -> Player:
        player.room_id = None
        return player

    async def update_disconnected_at(self, player: Player) -> Player:
        player.disconnected_at = datetime.now()
        return player

    async def update_sid(self, player: Player, sid: str) -> Player:
        player.latest_sid = sid
        return player
