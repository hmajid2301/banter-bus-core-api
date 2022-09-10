from datetime import datetime
from uuid import uuid4

from app.game_state.game_state_service import GameStateService
from app.player.player_exceptions import PlayerNotHostError
from app.room.room_exceptions import RoomHasNoHostError, RoomInInvalidState
from app.room.room_models import Room, RoomState
from app.room.room_repository import RoomRepository


class RoomService:
    def __init__(self, room_repository: RoomRepository) -> None:
        self.room_repository = room_repository

    async def create(self) -> Room:
        room_id = uuid4()

        room = Room(
            room_id=str(room_id),
            state=RoomState.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await self.room_repository.add(room)
        return room

    async def get(self, room_id: str) -> Room:
        room = await self.room_repository.get(id_=room_id)
        return room

    async def get_room_by_player_id(self, player_id: str) -> Room:
        room = await self.room_repository.get_room_by_player_id(player_id=player_id)
        return room

    async def update_host(self, room: Room, player_id: str):
        await self.room_repository.update_host(room=room, player_id=player_id)

    async def update_game_state(self, room: Room, new_room_state: RoomState):
        await self.room_repository.update_game_state(room=room, new_room_state=new_room_state)

    async def pause_game(
        self,
        room_id: str,
        player_id: str,
        game_state_service: GameStateService,
    ) -> int:
        room = await self.get(room_id=room_id)
        self._check_action_pause_action_is_valid(player_id, room)
        paused_for_seconds = await game_state_service.pause_game(room_id=room_id)
        return paused_for_seconds

    async def unpause_game(self, room_id: str, player_id: str, game_state_service: GameStateService) -> None:
        room = await self.get(room_id=room_id)
        self._check_action_pause_action_is_valid(player_id, room)
        await game_state_service.unpause_game(room_id=room_id)

    def _check_action_pause_action_is_valid(self, player_id: str, room: Room):
        self.check_is_player_host(room=room, player_id=player_id)
        if room.state is not RoomState.PLAYING:
            raise RoomInInvalidState("expected room to be in PLAYING state", room_state=room.state)

    @staticmethod
    def check_is_player_host(room: Room, player_id: str):
        host_id = room.host
        if not host_id:
            raise RoomHasNoHostError(msg="room has no host", room_id=room.room_id)
        elif host_id != player_id:
            raise PlayerNotHostError(
                msg="player is not host cannot kick player", player_id=player_id, host_player_id=room.host
            )
