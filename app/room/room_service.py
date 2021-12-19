import random
import string
from datetime import datetime
from uuid import uuid4

from fastapi import status

from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.exceptions import UnexpectedResponse
from app.room.room_exceptions import GameNotEnabled, GameNotFound
from app.room.room_models import GameState, Room
from app.room.room_repository import AbstractRoomRepository


class RoomService:
    def __init__(self, room_repository: AbstractRoomRepository) -> None:
        self.room_repoistory = room_repository

    async def create(self, game_name: str, management_client: AsyncGamesApi) -> Room:
        is_game_enabled = await self._is_enabled_game(game_name=game_name, management_client=management_client)
        if not is_game_enabled:
            raise GameNotEnabled(f"{game_name=} is not enabled")

        room_id = uuid4()
        room_code = await self._get_unused_room_code()

        room = Room(
            room_id=room_id,
            game_name=game_name,
            room_code=room_code,
            players=[],
            state=GameState.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await self.room_repoistory.add(room)
        return room

    @staticmethod
    async def _is_enabled_game(game_name: str, management_client: AsyncGamesApi) -> bool:
        try:
            game = await management_client.get_game(game_name=game_name)
            return game.enabled
        except UnexpectedResponse as e:
            status_code = e.status_code

            if status_code == status.HTTP_404_NOT_FOUND:
                raise GameNotFound(message=f"{game_name=} not found", e=e)
            else:
                raise e

    async def _get_unused_room_code(self) -> str:
        letters = string.ascii_uppercase
        used_room_codes = await self.room_repoistory.get_all_room_codes()

        new_room_code = ""
        while not new_room_code:
            room_code = "".join(random.choice(letters) for _ in range(5))

            if room_code not in used_room_codes:
                new_room_code = room_code

        return new_room_code
