from app.room.room_events_models import CreateRoom, RoomCreated
from app.room.room_factory import get_game_api, get_room_service


async def create_room(create_room_data: CreateRoom) -> RoomCreated:
    room_service = get_room_service()
    game_api_client = get_game_api()
    created_room = await room_service.create(game_name=create_room_data.game_name, management_client=game_api_client)
    return RoomCreated(room_code=created_room.room_code)
