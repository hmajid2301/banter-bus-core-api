from datetime import datetime, timedelta
from uuid import uuid4

from app.player.player_models import NewPlayer, Player
from app.room.room_models import Room
from app.room.room_repository import RoomRepository


class PlayerService:
    def __init__(self, room_repository: RoomRepository) -> None:
        self.room_repository = room_repository

    async def create(self, room: Room, new_player: NewPlayer) -> Player:
        player = Player(
            player_id=str(uuid4()),
            **new_player.dict(),
        )
        await self.room_repository.add_player(room, player)
        return player

    async def get(self, player_id: str) -> Player:
        player = await self.room_repository.get_player(player_id=player_id)
        return player

    async def get_by_sid(self, sid: str) -> Player:
        player = await self.room_repository.get_player_by_sid(sid=sid)
        return player

    async def get_all_in_room(self, room_id: str) -> list[Player]:
        return await self.room_repository.get_all_players(room_id=room_id)

    async def remove_from_room(self, room: Room, nickname: str) -> Player:
        return await self.room_repository.remove_player(room=room, nickname=nickname)

    async def update_disconnected_time(self, sid: str, disconnected_at: datetime | None = None):
        await self.room_repository.update_player_disconnected_at(sid=sid, disconnected_at=disconnected_at)

    async def update_latest_sid(self, player_id: str, latest_sid: str):
        await self.room_repository.update_sid(player_id=player_id, sid=latest_sid)

    async def disconnect_player(self, nickname: str, room_id: str, disconnect_timer_in_seconds: int) -> Player:
        player = await self.room_repository.get_player_by_nickname(room_id=room_id, nickname=nickname)
        if player.disconnected_at:
            now = datetime.now()
            disconnect_at = player.disconnected_at + timedelta(seconds=disconnect_timer_in_seconds)

            if disconnect_at <= now:
                room = await self.room_repository.get(id_=room_id)
                await self.remove_from_room(nickname=player.nickname, room=room)

        return player
