from datetime import datetime

from omnibus.log.logger import get_logger

from app.main import sio
from app.player.player_exceptions import PlayerNotFound
from app.player.player_factory import get_player_service
from app.room.lobby.lobby_event_handlers import (
    join_room,
    kick_player,
    rejoin_room,
    start_game,
)
from app.room.lobby.lobby_events_models import (
    HOST_DISCONNECTED,
    JOIN_ROOM,
    KICK_PLAYER,
    PLAYER_DISCONNECTED,
    REJOIN_ROOM,
    START_GAME,
    HostDisconnected,
    PlayerDisconnected,
)
from app.room.room_event_handlers import (
    create_room,
    get_next_question,
    pause_game,
    permanently_disconnect_player,
)
from app.room.room_events_models import (
    CREATE_ROOM,
    GET_NEXT_QUESTION,
    PAUSE_GAME,
    PERMANENTLY_DISCONNECT_PLAYER,
)
from app.room.room_factory import get_lobby_service, get_room_service


@sio.event
async def connect(sid, environ, auth):
    logger = get_logger()
    logger.debug("Player connected", sid=sid)


@sio.event
async def disconnect(sid):
    logger = get_logger()
    logger.debug("Player disconnected", sid=sid)
    player_service = get_player_service()
    try:
        player = await player_service.get_by_sid(sid=sid)
        player = await player_service.update_disconnected_time(player=player, disconnected_at=datetime.now())
    except PlayerNotFound:
        logger.warning("Failed to find player", sid=sid, exc_info=True)
        return

    logger.debug("Player found", player=player.dict(exclude={"avatar"}))
    if player.room_id:
        player_disconnected = PlayerDisconnected(nickname=player.nickname, avatar=player.avatar)
        room_service = get_room_service()
        lobby_service = get_lobby_service()
        room = await room_service.get(room_id=player.room_id)
        if room.host == player.player_id:
            new_host = await lobby_service.update_host(room=room, old_host_id=player.player_id)
            host_disconnected = HostDisconnected(new_host_nickname=new_host.nickname)
            await sio.emit(HOST_DISCONNECTED, host_disconnected.dict(), room=room.room_id)

        await sio.emit(PLAYER_DISCONNECTED, player_disconnected.dict(), room=room.room_id)


sio.on(CREATE_ROOM, create_room)
sio.on(JOIN_ROOM, join_room)
sio.on(REJOIN_ROOM, rejoin_room)
sio.on(KICK_PLAYER, kick_player)
sio.on(PERMANENTLY_DISCONNECT_PLAYER, permanently_disconnect_player)
sio.on(START_GAME, start_game)
sio.on(GET_NEXT_QUESTION, get_next_question)
sio.on(PAUSE_GAME, pause_game)
