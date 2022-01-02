import random
import string
from datetime import datetime
from http import HTTPStatus
from typing import List
from uuid import uuid4

from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.exceptions import UnexpectedResponse
from app.player.player_models import NewPlayer, Player, RoomPlayers
from app.player.player_service import PlayerService
from app.room.room_exceptions import (
    GameNotEnabled,
    GameNotFound,
    NicknameExistsException,
)
from app.room.room_models import Room, RoomState
from app.room.room_repository import AbstractRoomRepository


class RoomService:
    def __init__(self, room_repository: AbstractRoomRepository) -> None:
        self.room_repository = room_repository

    async def create(self, game_name: str, management_client: AsyncGamesApi) -> Room:
        is_game_enabled = await self._is_enabled_game(game_name=game_name, management_client=management_client)
        if not is_game_enabled:
            raise GameNotEnabled(f"{game_name=} is not enabled")

        room_id = uuid4()
        room_code = await self._get_unused_room_code()

        room = Room(
            room_id=str(room_id),
            game_name=game_name,
            room_code=room_code,
            state=RoomState.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await self.room_repository.add(room)
        return room

    @staticmethod
    async def _is_enabled_game(game_name: str, management_client: AsyncGamesApi) -> bool:
        try:
            game = await management_client.get_game(game_name=game_name)
            return game.enabled
        except UnexpectedResponse as e:
            status_code = e.status_code

            if status_code == HTTPStatus.NOT_FOUND:
                raise GameNotFound(message=f"{game_name=} not found", e=e)
            else:
                raise e

    async def _get_unused_room_code(self) -> str:
        letters = string.ascii_uppercase
        used_room_codes = await self.room_repository.get_all_room_codes()

        new_room_code = ""
        while not new_room_code:
            room_code = "".join(random.choice(letters) for _ in range(5))

            if room_code not in used_room_codes:
                new_room_code = room_code

        return new_room_code

    async def join(self, player_service: PlayerService, room_code: str, new_player: NewPlayer) -> RoomPlayers:
        room = await self._get_open_room(room_code=room_code)
        existing_players = await player_service.get_all_in_room(room_id=room.room_id)
        matching_nickname = [player for player in existing_players if player.nickname == new_player.nickname]
        if matching_nickname:
            raise NicknameExistsException(msg="nickname already exists", nickname=new_player.nickname)

        player = await player_service.create(room_id=room.room_id, new_player=new_player)
        if room.host is None:
            await self.room_repository.update_host(room=room, player_id=player.player_id)

        room_players = self._get_room_players(
            room_host_player_id=room.host or "", existing_players=existing_players, new_player=player
        )
        return room_players

    @staticmethod
    def _get_room_players(room_host_player_id: str, existing_players: List[Player], new_player: Player):
        players = [new_player, *existing_players]
        room_host_player = next(player for player in players if player.player_id == room_host_player_id)
        room_players = RoomPlayers(players=players, host_player_nickname=room_host_player.nickname)
        return room_players

    async def _get_open_room(self, room_code: str) -> Room:
        room = await self.room_repository.get_open_room(room_code=room_code)
        return room
