import random
import string
from datetime import datetime
from typing import List
from uuid import uuid4

from app.player.player_models import NewPlayer, Player, RoomPlayers
from app.player.player_service import PlayerService
from app.room.room_exceptions import NicknameExistsException
from app.room.room_models import Room, RoomState
from app.room.room_repository import AbstractRoomRepository


class RoomService:
    def __init__(self, room_repository: AbstractRoomRepository) -> None:
        self.room_repository = room_repository

    async def create(self) -> Room:
        room_id = uuid4()
        room_code = await self._get_room_code()

        room = Room(
            room_id=str(room_id),
            room_code=room_code,
            state=RoomState.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await self.room_repository.add(room)
        return room

    async def _get_room_code(self) -> str:
        available_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        used_room_codes = await self.room_repository.get_all_room_codes()

        room_code = ""
        while not room_code:
            possible_room_code = "".join(random.choice(available_chars) for _ in range(12))

            if possible_room_code not in used_room_codes:
                room_code = possible_room_code

        return room_code

    async def get(self, room_id: str) -> Room:
        room = await self.room_repository.get(id_=room_id)
        return room

    async def join(self, player_service: PlayerService, room_code: str, new_player: NewPlayer) -> RoomPlayers:
        room = await self._get_by_room_code(room_code=room_code)
        existing_players = await player_service.get_all_in_room(room_id=room.room_id)
        self._check_nickname_is_unique(new_player_nickname=new_player.nickname, existing_players=existing_players)

        player = await self._add_new_player(player_service=player_service, new_player=new_player, room=room)
        room_players = self._get_room_players(
            room_host_player_id=room.host or "",
            existing_players=existing_players,
            new_player=player,
            room_code=room.room_code,
        )
        return room_players

    async def rejoin(self, player_service: PlayerService, player_id: str) -> RoomPlayers:
        player = await player_service.get(player_id=player_id)
        room = await self.room_repository.get(id_=player.room_id)
        existing_players = await player_service.get_all_in_room(room_id=player.room_id)

        room_players = self._get_room_players(
            room_host_player_id=room.host or "",
            existing_players=existing_players,
            new_player=player,
            room_code=room.room_code,
        )
        return room_players

    async def _get_by_room_code(self, room_code: str) -> Room:
        room = await self.room_repository.get_by_room_code(room_code=room_code)
        return room

    @staticmethod
    def _check_nickname_is_unique(new_player_nickname: str, existing_players: List[Player]):
        matching_nickname = [player for player in existing_players if player.nickname == new_player_nickname]
        if matching_nickname:
            raise NicknameExistsException(msg="nickname already exists", nickname=new_player_nickname)

    async def _add_new_player(self, player_service: PlayerService, new_player: NewPlayer, room: Room):
        player = await player_service.create(room_id=room.room_id, new_player=new_player)
        if room.host is None:
            await self.room_repository.update_host(room=room, player_id=player.player_id)
        return player

    @staticmethod
    def _get_room_players(room_host_player_id: str, existing_players: List[Player], new_player: Player, room_code: str):
        players = [*existing_players, new_player]
        room_host_player = next(player for player in players if player.player_id == room_host_player_id)
        room_players = RoomPlayers(
            players=players,
            host_player_nickname=room_host_player.nickname,
            player_id=new_player.player_id,
            room_code=room_code,
        )
        return room_players
