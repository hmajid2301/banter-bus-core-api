from datetime import datetime, timedelta
from typing import List, Optional
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
            latest_sid=new_player.latest_sid,
            room_id=room_id,
        )
        await self.player_repository.add(player)
        return player

    async def get(self, player_id: str) -> Player:
        player = await self.player_repository.get(id_=player_id)
        return player

    async def get_all_in_room(self, room_id: str) -> List[Player]:
        players = await self.player_repository.get_all_in_room(room_id=room_id)
        return players

    async def remove_from_room(self, nickname: str, room_id: str) -> Player:
        player = await self.player_repository.get_by_nickname(nickname=nickname, room_id=room_id)
        await self.player_repository.remove_from_room(player=player)
        return player

    async def update_disconnected_time(self, player: Player, disconnected_at: Optional[datetime] = None) -> Player:
        player = await self.player_repository.update_disconnected_at(player=player, disconnected_at=disconnected_at)
        return player

    async def update_latest_sid(self, player: Player, latest_sid: str) -> Player:
        player = await self.player_repository.update_sid(player=player, sid=latest_sid)
        return player

    async def disconnect_player(self, nickname: str, room_id: str, disconnect_timer_in_seconds: int) -> Player:
        player = await self.player_repository.get_by_nickname(room_id=room_id, nickname=nickname)
        if player.disconnected_at and player.room_id:
            now = datetime.now()
            disconnect_at = player.disconnected_at + timedelta(seconds=disconnect_timer_in_seconds)

            if disconnect_at <= now:
                await self.remove_from_room(nickname=player.nickname, room_id=player.room_id)

        return player
