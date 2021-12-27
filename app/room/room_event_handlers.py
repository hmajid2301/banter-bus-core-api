from app.core.logger import get_logger
from app.main import socket_manager as sm
from app.room.room_events_models import CreateRoom, Error, RoomCreated
from app.room.room_factory import get_game_api, get_room_service


@sm.on("CREATE_ROOM")
async def create_room_event(sid, *args, **kwargs):
    create_room_data = CreateRoom(**args[0])
    logger = get_logger()
    logger.debug("creating room")
    try:
        room_service = get_room_service()
        game_api_client = get_game_api()
        created_room = await room_service.create(
            game_name=create_room_data.game_name, management_client=game_api_client
        )
        room_created = RoomCreated(**created_room.dict())
        await sm.emit("ROOM_CREATED", room_created.dict())
        logger.debug("room created", room_created=room_created.dict())
    except Exception:
        logger.exception("failed to create room")
        error = Error(code="room_create_fail", message="failed to create room")
        await sm.emit("ERROR", error.dict())
