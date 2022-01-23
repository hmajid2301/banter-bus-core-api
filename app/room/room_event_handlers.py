from typing import List

from omnibus.log.logger import get_logger
from pydantic import parse_obj_as

from app.main import sio
from app.player.player_exceptions import PlayerNotHostError
from app.player.player_factory import get_player_service
from app.player.player_models import NewPlayer, RoomPlayers
from app.room.room_events_models import (
    CREATE_ROOM,
    ERROR,
    JOIN_ROOM,
    KICK_PLAYER,
    NEW_ROOM_JOINED,
    PLAYER_KICKED,
    REJOIN_ROOM,
    ROOM_CREATED,
    ROOM_JOINED,
    Error,
    JoinRoom,
    KickPlayer,
    NewRoomJoined,
    Player,
    PlayerKicked,
    RejoinRoom,
    RoomCreated,
    RoomJoined,
)
from app.room.room_exceptions import (
    NicknameExistsException,
    RoomInInvalidState,
    RoomNotFound,
)
from app.room.room_factory import get_room_service


@sio.on(CREATE_ROOM)
async def create_room(sid, *args):
    logger = get_logger()
    logger.debug(CREATE_ROOM)
    try:
        room_service = get_room_service()
        created_room = await room_service.create()
        room_created = RoomCreated(**created_room.dict())
        await sio.emit(ROOM_CREATED, room_created.dict())
        logger.debug("room created", room_created=room_created.dict(), room=sid)
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
        new_room_joined = NewRoomJoined(player_id=room_players.player_id)
        await sio.emit(NEW_ROOM_JOINED, new_room_joined.dict(), room=sid)
        logger.debug(ROOM_JOINED, room_joined=room_joined.dict())
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="room_join_fail", message="room not found")
        await sio.emit(ERROR, error.dict())
    except NicknameExistsException as e:
        logger.exception("nickname already exists", room_code=join_room.room_code, nickname=e.nickname)
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
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="room_join_fail", message="room not found")
        await sio.emit(ERROR, error.dict())
    except Exception:
        logger.exception("failed to rejoin room", sid=sid)
        error = Error(code="room_join_fail", message="failed to rejoin room")
        await sio.emit(ERROR, error.dict())


async def _publish_room_joined(sid: str, room_code: str, room_players: RoomPlayers) -> RoomJoined:
    players = parse_obj_as(List[Player], room_players.players)
    room_joined = RoomJoined(players=players, host_player_nickname=room_players.host_player_nickname)
    sio.enter_room(sid, room_code)
    await sio.emit(ROOM_JOINED, data=room_joined.dict(), room=room_code)
    return room_joined


@sio.on(KICK_PLAYER)
async def kick_player(sid, *args):
    logger = get_logger()
    logger.debug(KICK_PLAYER, player_id=sid)
    try:
        kick_player = KickPlayer(**args[0])
        room_service = get_room_service()
        player_service = get_player_service()

        player_kicked_nickname = await room_service.kick_player(
            player_service=player_service,
            player_to_kick_nickname=kick_player.kick_player_nickname,
            player_attempting_kick=kick_player.player_id,
            room_code=kick_player.room_code,
        )
        player_kicked = PlayerKicked(nickname=player_kicked_nickname)
        logger.debug(PLAYER_KICKED, player_kicked=player_kicked.dict())
        await sio.emit(PLAYER_KICKED, data=player_kicked.dict(), room=kick_player.room_code)
    except RoomInInvalidState as e:
        logger.exception("Game has started playing cannot kick players", room_state=e.room_state)
        error = Error(code="kick_player_fail", message="The game has started playing, so cannot kick player")
        await sio.emit(ERROR, error.dict())
    except PlayerNotHostError as e:
        logger.exception("player is not host so cannot kick", player_id=e.player_id, host_player_id=e.host_player_id)
        error = Error(code="kick_player_fail", message="You are not host, so cannot kick another player")
        await sio.emit(ERROR, error.dict())
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="kick_player_fail", message="Room not found")
        await sio.emit(ERROR, error.dict())
    except Exception:
        logger.exception("failed to kick player", kick_player=kick_player)
        error = Error(code="kick_player_fail", message="Failed to kick player")
        await sio.emit(ERROR, error.dict())
