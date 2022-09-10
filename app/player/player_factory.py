from app.player.player_service import PlayerService
from app.room.room_repository import RoomRepository


def get_room_repository() -> RoomRepository:
    return RoomRepository()


def get_player_service() -> PlayerService:
    room_repository = get_room_repository()
    return PlayerService(room_repository=room_repository)
