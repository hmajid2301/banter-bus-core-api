from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.api_client import ApiClient
from app.core.config import get_settings
from app.room.room_repository import AbstractRoomRepository, RoomRepository
from app.room.room_service import RoomService


def get_room_repository() -> AbstractRoomRepository:
    return RoomRepository()


def get_room_service() -> RoomService:
    room_repository = get_room_repository()
    room_service = RoomService(room_repository=room_repository)
    return room_service


def get_game_api() -> AsyncGamesApi:
    settings = get_settings()
    api_host = settings.get_management_url()
    api_client = ApiClient(host=api_host)
    game_api_client = AsyncGamesApi(api_client=api_client)
    return game_api_client
