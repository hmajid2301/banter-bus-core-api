from typing import Tuple

from omnibus.log.logger import get_logger

from app.core.config import get_settings
from app.event_manager import error_handler, event_handler, leave_room
from app.exception_handlers import handle_error
from app.player.player_factory import get_player_service
from app.room.room_events_models import (
    CreateRoom,
    PermanentlyDisconnectedPlayer,
    PermanentlyDisconnectPlayer,
    RoomCreated,
)
from app.room.room_exceptions import RoomNotFound
from app.room.room_factory import get_room_service


@event_handler(input_model=CreateRoom)
@error_handler(Exception, handle_error)
async def create_room(sid: str, _: CreateRoom) -> Tuple[RoomCreated, None]:
    room_service = get_room_service()
    created_room = await room_service.create()
    room_created = RoomCreated(room_code=created_room.room_id)
    return room_created, None


@event_handler(input_model=PermanentlyDisconnectPlayer)
@error_handler(Exception, handle_error)
async def permanently_disconnect_player(
    _: str, data: PermanentlyDisconnectPlayer
) -> Tuple[PermanentlyDisconnectedPlayer, str]:
    logger = get_logger()

    try:
        config = get_settings()
        player_service = get_player_service()
        room_service = get_room_service()

        room = await room_service.get(room_id=data.room_code)
        await room_service.update_player_count(room, increment=False)
        disconnected_player = await player_service.disconnect_player(
            nickname=data.nickname,
            room_id=data.room_code,
            disconnect_timer_in_seconds=config.DISCONNECT_TIMER_IN_SECONDS,
        )

        if not disconnected_player.room_id:
            logger.warning("Player already disconnected ", player_id=disconnected_player.player_id)
            raise Exception("Unexpected state player already disconnected")

        leave_room(disconnected_player.latest_sid, room=disconnected_player.room_id)
        perm_disconnected_player = PermanentlyDisconnectedPlayer(nickname=data.nickname)
        return perm_disconnected_player, data.room_code
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        raise e
