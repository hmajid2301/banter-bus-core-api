from datetime import datetime
from typing import List
from uuid import uuid4

from app.clients.management_api.api.games_api import AsyncGamesApi
from app.core.exceptions import NoOtherHostError
from app.player.player_exceptions import PlayerHasNoRoomError, PlayerNotHostError
from app.player.player_models import NewPlayer, Player, RoomPlayers
from app.player.player_service import PlayerService
from app.room.room_exceptions import (
    GameNotEnabled,
    NicknameExistsException,
    RoomHasNoHostError,
    RoomInInvalidState,
    RoomNotJoinableError,
)
from app.room.room_models import Room, RoomState
from app.room.room_repository import AbstractRoomRepository


class RoomService:
    def __init__(self, room_repository: AbstractRoomRepository) -> None:
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

    async def join(self, player_service: PlayerService, room_id: str, new_player: NewPlayer) -> RoomPlayers:
        room = await self.room_repository.get(id_=room_id)
        existing_players = await player_service.get_all_in_room(room_id=room.room_id)
        self._check_nickname_is_unique(new_player_nickname=new_player.nickname, existing_players=existing_players)

        player = await self._add_new_player(player_service=player_service, new_player=new_player, room=room)
        players = [*existing_players, player]

        if not room.state.is_room_joinable:
            raise RoomNotJoinableError(msg="room is not joinable", room_id=room.room_id, room_state=room.state)
        if not room.host:
            raise RoomHasNoHostError(msg="room has no host", room_id=room.room_id)

        room_players = self._get_room_players(
            room_host_player_id=room.host,
            players=players,
            player_id=player.player_id,
            room_code=room.room_id,
        )
        return room_players

    async def rejoin(self, player_service: PlayerService, player_id: str, latest_sid: str) -> RoomPlayers:
        player = await player_service.get(player_id=player_id)
        player = await player_service.update_latest_sid(player=player, latest_sid=latest_sid)

        if not player.room_id:
            raise PlayerHasNoRoomError("player has no room id")

        # TODO: use method in player service in future
        player.disconnected_at = None
        room = await self.room_repository.get(id_=player.room_id)
        existing_players = await player_service.get_all_in_room(room_id=player.room_id)

        if not room.state.is_room_joinable:
            raise RoomNotJoinableError(msg="room is not joinable", room_id=room.room_id, room_state=room.state)
        if not room.host:
            raise RoomHasNoHostError(msg="room has no host", room_id=room.room_id)

        room_players = self._get_room_players(
            room_host_player_id=room.host,
            players=existing_players,
            player_id=player.player_id,
            room_code=room.room_id,
        )
        return room_players

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
    def _get_room_players(
        room_host_player_id: str,
        players: List[Player],
        player_id: str,
        room_code: str,
    ) -> RoomPlayers:
        room_host_player = next(player for player in players if player.player_id == room_host_player_id)
        room_players = RoomPlayers(
            players=players,
            host_player_nickname=room_host_player.nickname,
            player_id=player_id,
            room_code=room_code,
        )
        return room_players

    async def kick_player(
        self, player_service: PlayerService, player_to_kick_nickname: str, player_attempting_kick: str, room_id: str
    ) -> Player:
        room = await self.room_repository.get(id_=room_id)
        self._check_is_player_host(room=room, player_id=player_attempting_kick)

        if room.state != RoomState.CREATED:
            raise RoomInInvalidState(msg=f"expected room state {RoomState.CREATED}", room_state=room.state)

        player = await player_service.remove_from_room(nickname=player_to_kick_nickname, room_id=room.room_id)
        return player

    async def update_host(self, player_service: PlayerService, room: Room, old_host_id: str) -> Player:
        players = await player_service.get_all_in_room(room_id=room.room_id)

        for player in players:
            if not player.player_id == old_host_id:
                await self.room_repository.update_host(room=room, player_id=player.player_id)

                return player

        raise NoOtherHostError(f"no other host found for room {room.room_id=}")

    async def start_game(self, game_api: AsyncGamesApi, game_name: str, player_id: str, room_id: str) -> Room:
        room = await self.room_repository.get(id_=room_id)
        if room.state != RoomState.CREATED:
            raise RoomInInvalidState(msg=f"expected room state {RoomState.CREATED}", room_state=room.state)

        self._check_is_player_host(room=room, player_id=player_id)

        game = await game_api.get_game(game_name=game_name)
        if not game.enabled:
            raise GameNotEnabled(f"{game_name} is not enabled")

        await self.room_repository.update_game_state(room=room, new_room_state=RoomState.PLAYING)
        return room

    @staticmethod
    def _check_is_player_host(room: Room, player_id: str):
        host_id = room.host
        if not host_id:
            raise RoomHasNoHostError(msg="room has no host", room_id=room.room_id)
        elif host_id != player_id:
            raise PlayerNotHostError(
                msg="player is not host cannot kick player", player_id=player_id, host_player_id=room.host
            )
