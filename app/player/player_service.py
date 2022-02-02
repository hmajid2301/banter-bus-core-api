from datetime import datetime, timedelta
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
        await self.player_repository.remove_room(player=player)
        return player

    async def update_disconnected_time(self, sid: str) -> Player:
        player = await self.player_repository.get_by_sid(sid=sid)
        player = await self.player_repository.update_disconnected_at(player=player)
        return player

    async def update_latest_sid(self, player: Player, latest_sid: str) -> Player:
        player = await self.player_repository.update_sid(player=player, sid=latest_sid)
        return player

    async def disconnect_players(self, disconnect_timer_in_minutes) -> List[Player]:
        players = await self.player_repository.get_disconnect()
        disconnected_player: List[Player] = []

        wait_time = timedelta(minutes=disconnect_timer_in_minutes)
        now = datetime.now()

        for player in players:
            if (player.disconnected_at) and (player.room_id) and (now - wait_time > player.disconnected_at):
                await self.remove_from_room(nickname=player.nickname, room_id=player.room_id)
                disconnected_player.append(player)

        return disconnected_player
