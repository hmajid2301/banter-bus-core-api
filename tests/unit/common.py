from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.api_client import ApiClient
from app.player.player_models import Player
from app.player.player_service import PlayerService
from app.room.room_models import Room
from app.room.room_service import RoomService
from tests.unit.factories import PlayerFactory, RoomFactory
from tests.unit.player.fake_player_repository import FakePlayerRepository
from tests.unit.room.fake_room_repository import FakeRoomRepository


def get_player_service(players: list[Player] = [], num: int = 1, **kwargs) -> PlayerService:
    if players:
        existing_players = players
    elif num:
        existing_players = PlayerFactory.build_batch(num, **kwargs)
    else:
        existing_players = []

    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)
    return player_service


def get_room_service(rooms: list[Room] = [], num: int = 1, **kwargs) -> RoomService:
    if rooms:
        existing_room = rooms
    elif num:
        existing_room = RoomFactory.build_batch(num, **kwargs)
    else:
        existing_room = []

    room_repository = FakeRoomRepository(rooms=existing_room)
    room_service = RoomService(room_repository=room_repository)
    return room_service


def get_game_api_client() -> AsyncGamesApi:
    api_client = ApiClient(host="http://localhost")
    game_api = AsyncGamesApi(api_client=api_client)
    return game_api
