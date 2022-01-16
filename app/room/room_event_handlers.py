from typing import List

from omnibus.log.logger import get_logger
from pydantic import parse_obj_as

from app.main import sio
from app.player.player_factory import get_player_service
from app.player.player_models import NewPlayer, RoomPlayers
from app.room.room_events_models import (
    CREATE_ROOM,
    ERROR,
    JOIN_ROOM,
    REJOIN_ROOM,
    ROOM_CREATED,
    ROOM_JOINED,
    Error,
    JoinRoom,
    Player,
    RejoinRoom,
    RoomCreated,
    RoomJoined,
)
from app.room.room_exceptions import NicknameExistsException
from app.room.room_factory import get_room_service


@sio.on(CREATE_ROOM)
async def create_room(_, *args):
    logger = get_logger()
    logger.debug(CREATE_ROOM)
    try:
        room_service = get_room_service()
        created_room = await room_service.create()
        room_created = RoomCreated(**created_room.dict())
        await sio.emit(ROOM_CREATED, room_created.dict())
        logger.debug("room created", room_created=room_created.dict())
    except Exception:
        logger.exception("failed to create room")
        error = Error(code="room_create_fail", message="failed to create room")
        await sio.emit(ERROR, error.dict())


@sio.on(JOIN_ROOM)
async def join_room(sid, *args):
    logger = get_logger()
    logger.debug(JOIN_ROOM, player_id=sid)
    try:
        join_room = JoinRoom(**args[0])
        room_service = get_room_service()
        player_service = get_player_service()
        new_player = NewPlayer(
            avatar=join_room.avatar,
            nickname=join_room.nickname,
        )
        room_players = await room_service.join(
            player_service=player_service, room_code=join_room.room_code, new_player=new_player
        )
        room_joined = await _publish_room_joined(sid, join_room.room_code, room_players)
        logger.debug(ROOM_JOINED, room_joined=room_joined.dict())
    except NicknameExistsException as e:
        logger.exception("nickname already exists", played_id=sid, nickname=e.nickname)
        error = Error(code="room_join_fail", message=f"nickname {e.nickname} already exists")
        await sio.emit(ERROR, error.dict())
    except Exception:
        logger.exception("failed to join room", sid=sid)
        error = Error(code="room_join_fail", message="failed to join room")
        await sio.emit(ERROR, error.dict())


@sio.on(REJOIN_ROOM)
async def rejoin_room(sid, *args):
    logger = get_logger()
    logger.debug(REJOIN_ROOM, player_id=sid)
    try:
        rejoin_room = RejoinRoom(**args[0])
        room_service = get_room_service()
        player_service = get_player_service()
        room_players = await room_service.rejoin(player_service=player_service, player_id=rejoin_room.player_id)
        room_joined = await _publish_room_joined(sid, room_players.room_code, room_players)
        logger.debug(ROOM_JOINED, room_joined=room_joined.dict())
    except Exception:
        logger.exception("failed to rejoin room", sid=sid)
        error = Error(code="room_join_fail", message="failed to rejoin room")
        await sio.emit(ERROR, error.dict())


async def _publish_room_joined(sid: str, room_code: str, room_players: RoomPlayers) -> RoomJoined:
    players = parse_obj_as(List[Player], room_players.players)
    room_joined = RoomJoined(
        players=players, host_player_nickname=room_players.host_player_nickname, player_id=room_players.player_id
    )
    sio.enter_room(sid, room_code)
    await sio.emit(ROOM_JOINED, data=room_joined.dict(), room=room_code)
    return room_joined
