from typing import List
from uuid import uuid4

from app.player.player_models import NewPlayer, Player
from app.player.player_repository import AbstractPlayerRepository


class PlayerService:
    def __init__(self, player_repository: AbstractPlayerRepository) -> None:
        self.player_repository = player_repository

    async def create(self, room_id: str, new_player: NewPlayer) -> Player:
        player_id = str(uuid4())
        player = Player(
            player_id=player_id,
            avatar=new_player.avatar,
            nickname=new_player.nickname,
            room_id=room_id,
        )
        await self.player_repository.add(player)
        return player

    async def get_all_in_room(self, room_id: str) -> List[Player]:
        players = await self.player_repository.get_all_in_room(room_id=room_id)
        return players
