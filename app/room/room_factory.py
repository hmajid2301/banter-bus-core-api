from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.api_client import ApiClient
from app.core.config import get_settings
from app.game_state.game_state_factory import get_game_state_service
from app.player.player_factory import get_player_service, get_room_repository
from app.room.lobby.lobby_service import LobbyService
from app.room.room_service import RoomService


def get_room_service() -> RoomService:
    room_repository = get_room_repository()
    return RoomService(room_repository=room_repository)


def get_lobby_service() -> LobbyService:
    room_service = get_room_service()
    game_state_service = get_game_state_service()
    player_service = get_player_service()
    return LobbyService(room_service=room_service, game_state_service=game_state_service, player_service=player_service)


def get_game_api() -> AsyncGamesApi:
    settings = get_settings()
    api_host = settings.get_management_url()
    api_client = ApiClient(host=api_host)
    return AsyncGamesApi(api_client=api_client)
