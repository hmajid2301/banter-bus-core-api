from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.models import GameOut
from app.core.exceptions import NoOtherHostError
from app.game_state.game_state_service import GameStateService
from app.player.player_exceptions import PlayerHasNoRoomError
from app.player.player_models import NewPlayer, Player, RoomPlayers
from app.player.player_service import PlayerService
from app.room.room_exceptions import (
    GameNotEnabled,
    NicknameExistsException,
    RoomHasNoHostError,
    RoomInInvalidState,
    RoomNotJoinableError,
    TooFewPlayersInRoomError,
    TooManyPlayersInRoomError,
)
from app.room.room_models import Room, RoomState
from app.room.room_service import RoomService


class LobbyService:
    def __init__(
        self, room_service: RoomService, player_service: PlayerService, game_state_service: GameStateService
    ) -> None:
        self.room_service = room_service
        self.player_service = player_service
        self.game_state_service = game_state_service

    async def create_room(self) -> Room:
        room = await self.room_service.create()
        return room

    async def join(self, room_id: str, new_player: NewPlayer) -> RoomPlayers:
        room = await self.room_service.get(room_id=room_id)
        if not room.state.is_room_joinable:
            raise RoomNotJoinableError(msg="room is not joinable", room_id=room.room_id, room_state=room.state)

        existing_players = await self.player_service.get_all_in_room(room_id=room.room_id)
        self._check_nickname_is_unique(new_player_nickname=new_player.nickname, existing_players=existing_players)

        player = await self._add_new_player(new_player=new_player, room=room)
        players = [*existing_players, player]

        if not room.host:
            raise RoomHasNoHostError(msg="room has no host", room_id=room.room_id)

        await self.room_service.update_player_count(room, increment=True)
        room_players = self._get_players_in_room(
            room_host_player_id=room.host,
            players=players,
            player_id=player.player_id,
            room_code=room.room_id,
        )
        return room_players

    @staticmethod
    def _check_nickname_is_unique(new_player_nickname: str, existing_players: list[Player]):
        matching_nickname = [player for player in existing_players if player.nickname == new_player_nickname]
        if matching_nickname:
            raise NicknameExistsException(msg="nickname already exists", nickname=new_player_nickname)

    async def _add_new_player(self, new_player: NewPlayer, room: Room):
        player = await self.player_service.create(room_id=room.room_id, new_player=new_player)
        if room.host is None:
            await self.room_service.update_host(room=room, player_id=player.player_id)
        return player

    async def rejoin(self, player_id: str, latest_sid: str) -> RoomPlayers:
        player = await self.player_service.get(player_id=player_id)
        player = await self.player_service.update_latest_sid(player=player, latest_sid=latest_sid)

        if not player.room_id:
            raise PlayerHasNoRoomError("player has no room id")

        await self.player_service.update_disconnected_time(player=player, disconnected_at=None)
        room = await self.room_service.get(room_id=player.room_id)
        existing_players = await self.player_service.get_all_in_room(room_id=player.room_id)

        if not room.state.is_room_rejoinable:
            raise RoomNotJoinableError(msg="room is not rejoinable", room_id=room.room_id, room_state=room.state)
        if not room.host:
            raise RoomHasNoHostError(msg="room has no host", room_id=room.room_id)

        room_players = self._get_players_in_room(
            room_host_player_id=room.host,
            players=existing_players,
            player_id=player.player_id,
            room_code=room.room_id,
        )
        return room_players

    @staticmethod
    def _get_players_in_room(
        room_host_player_id: str,
        players: list[Player],
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

    async def kick_player(self, player_to_kick_nickname: str, player_attempting_kick: str, room_id: str) -> Player:
        room = await self.room_service.get(room_id=room_id)
        self.room_service.check_is_player_host(room=room, player_id=player_attempting_kick)

        if room.state != RoomState.CREATED:
            raise RoomInInvalidState(msg=f"expected room state {RoomState.CREATED}", room_state=room.state)

        player = await self.player_service.remove_from_room(nickname=player_to_kick_nickname, room_id=room.room_id)
        await self.room_service.update_player_count(room, increment=False)
        return player

    async def update_host(self, room: Room, old_host_id: str) -> Player:
        players = await self.player_service.get_all_in_room(room_id=room.room_id)

        for player in players:
            if not player.player_id == old_host_id:
                await self.room_service.update_host(room=room, player_id=player.player_id)

                return player

        raise NoOtherHostError(f"no other host found for room {room.room_id=}")

    async def start_game(self, game_api: AsyncGamesApi, game_name: str, player_id: str, room_id: str) -> Room:
        room = await self.room_service.get(room_id=room_id)
        if room.state != RoomState.CREATED:
            raise RoomInInvalidState(msg=f"expected room state {RoomState.CREATED}", room_state=room.state)

        self.room_service.check_is_player_host(room=room, player_id=player_id)
        game = await game_api.get_game(game_name=game_name)
        self._check_game_is_valid(game_name, room, game)

        await self.room_service.update_game_state(room=room, new_room_state=RoomState.PLAYING)
        players = await self.player_service.get_all_in_room(room_id=room.room_id)
        await self.game_state_service.create(room_id=room.room_id, players=players, game_name=game.name)
        return room

    @staticmethod
    def _check_game_is_valid(game_name: str, room: Room, game: GameOut):
        if not game.enabled:
            raise GameNotEnabled(f"{game_name} is not enabled")
        elif room.player_count > game.maximum_players:
            raise TooManyPlayersInRoomError(
                "too many players in the room to play game",
                game_name=game_name,
                room_id=room.room_id,
                room_player_count=room.player_count,
                game_maximum_players=game.maximum_players,
            )
        elif room.player_count < game.minimum_players:
            raise TooFewPlayersInRoomError(
                "too few players in the room to play game",
                game_name=game_name,
                room_id=room.room_id,
                room_player_count=room.player_count,
                game_minimum_players=game.minimum_players,
            )
