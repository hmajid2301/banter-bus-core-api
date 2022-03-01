from typing import List

from omnibus.log.logger import get_logger
from pydantic import parse_obj_as

from app.core.config import get_settings
from app.main import sio
from app.model_validator import validate
from app.player.player_exceptions import PlayerHasNoRoomError, PlayerNotHostError
from app.player.player_factory import get_player_service
from app.player.player_models import NewPlayer, RoomPlayers
from app.room.room_events_models import (
    CREATE_ROOM,
    ERROR,
    JOIN_ROOM,
    KICK_PLAYER,
    NEW_ROOM_JOINED,
    PERMANENTLY_DISCONNECT_PLAYER,
    PERMANENTLY_DISCONNECTED_PLAYER,
    PLAYER_KICKED,
    REJOIN_ROOM,
    ROOM_CREATED,
    ROOM_JOINED,
    CreateRoom,
    Error,
    JoinRoom,
    KickPlayer,
    NewRoomJoined,
    PermanentlyDisconnectedPlayer,
    PermanentlyDisconnectPlayer,
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


async def handle_error(sid, error_code):
    logger = get_logger()
    logger.exception("Failed action", error_code=error_code)
    error = Error(code=error_code, message="An unexpected error occurred on the server")
    await sio.emit(ERROR, error.dict(), room=sid)


@validate(CreateRoom, handle_error, "room_create_fail")
async def create_room(sid, data: CreateRoom):
    logger = get_logger()
    logger.debug(CREATE_ROOM)

    room_service = get_room_service()
    created_room = await room_service.create()
    room_created = RoomCreated(room_code=created_room.room_id)
    await sio.emit(ROOM_CREATED, room_created.dict())
    logger.debug("room created", room_created=room_created.dict(), room=sid)


@validate(JoinRoom, handle_error, "room_join_fail")
async def join_room(sid, data: JoinRoom):
    logger = get_logger()
    logger.debug(JOIN_ROOM, player_id=sid)
    try:
        room_service = get_room_service()
        player_service = get_player_service()
        new_player = NewPlayer(
            avatar=data.avatar,
            nickname=data.nickname,
            latest_sid=sid,
        )
        room_players = await room_service.join(
            player_service=player_service, room_id=data.room_code, new_player=new_player
        )
        room_joined = await _publish_room_joined(sid, data.room_code, room_players)
        new_room_joined = NewRoomJoined(player_id=room_players.player_id)
        await sio.emit(NEW_ROOM_JOINED, new_room_joined.dict(), room=sid)
        avatar_excludes = {idx: {"avatar"} for idx in range(len(room_joined.players))}
        logger.debug(ROOM_JOINED, room_joined=room_joined.dict(exclude={"players": avatar_excludes}))
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="room_join_fail", message="room not found")
        await sio.emit(ERROR, error.dict(), room=sid)
    except NicknameExistsException as e:
        logger.exception("nickname already exists", room_code=data.room_code, nickname=e.nickname)
        error = Error(code="room_join_fail", message=f"nickname {e.nickname} already exists")
        await sio.emit(ERROR, error.dict(), room=sid)


@validate(RejoinRoom, handle_error, "room_join_fail")
async def rejoin_room(sid, data: RejoinRoom):
    logger = get_logger()
    logger.debug(REJOIN_ROOM, player_id=sid)
    try:
        room_service = get_room_service()
        player_service = get_player_service()
        room_players = await room_service.rejoin(
            player_service=player_service, player_id=data.player_id, latest_sid=sid
        )
        room_joined = await _publish_room_joined(sid, room_players.room_code, room_players)
        avatar_excludes = {idx: {"avatar"} for idx in range(len(room_joined.players))}
        logger.debug(ROOM_JOINED, room_joined=room_joined.dict(exclude={"players": avatar_excludes}))
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="room_join_fail", message="room not found")
        await sio.emit(ERROR, error.dict(), room=sid)
    except PlayerHasNoRoomError:
        logger.exception("player has no room, they were likely disconnected from said room", player_id=data.player_id)
        error = Error(code="room_join_fail", message="disconnected from room, please re-join with a new nickname")
        await sio.emit(ERROR, error.dict(), room=sid)


async def _publish_room_joined(sid: str, room_code: str, room_players: RoomPlayers) -> RoomJoined:
    players = parse_obj_as(List[Player], room_players.players)
    room_joined = RoomJoined(players=players, host_player_nickname=room_players.host_player_nickname)
    sio.enter_room(sid, room_code)
    await sio.emit(ROOM_JOINED, data=room_joined.dict(), room=room_code)
    return room_joined


@validate(KickPlayer, handle_error, "kick_player_fail")
async def kick_player(sid, data: KickPlayer):
    logger = get_logger()
    logger.debug(KICK_PLAYER, player_id=sid)
    try:
        room_service = get_room_service()
        player_service = get_player_service()

        kicked_player = await room_service.kick_player(
            player_service=player_service,
            player_to_kick_nickname=data.kick_player_nickname,
            player_attempting_kick=data.player_id,
            room_id=data.room_code,
        )
        player_kicked = PlayerKicked(nickname=kicked_player.nickname)
        logger.debug(PLAYER_KICKED, player_kicked=player_kicked.dict())
        await sio.emit(PLAYER_KICKED, data=player_kicked.dict(), room=data.room_code)
        sio.leave_room(kicked_player.latest_sid, room=data.room_code)
    except RoomInInvalidState as e:
        logger.exception("Game has started playing cannot kick players", room_state=e.room_state)
        error = Error(code="kick_player_fail", message="The game has started playing, so cannot kick player")
        await sio.emit(ERROR, error.dict(), room=sid)
    except PlayerNotHostError as e:
        logger.exception("player is not host so cannot kick", player_id=e.player_id, host_player_id=e.host_player_id)
        error = Error(code="kick_player_fail", message="You are not host, so cannot kick another player")
        await sio.emit(ERROR, error.dict(), room=sid)
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="kick_player_fail", message="Room not found")
        await sio.emit(ERROR, error.dict(), room=sid)


@validate(PermanentlyDisconnectPlayer, handle_error, "disconnect_player_fail")
async def permanently_disconnect_player(sid, data: PermanentlyDisconnectPlayer):
    logger = get_logger()
    logger.debug(PERMANENTLY_DISCONNECT_PLAYER, player_id=sid)
    config = get_settings()
    try:
        player_service = get_player_service()
        disconnected_player = await player_service.disconnect_player(
            nickname=data.nickname,
            room_id=data.room_code,
            disconnect_timer_in_seconds=config.DISCONNECT_TIMER_IN_SECONDS,
        )

        perm_disconnected_player = PermanentlyDisconnectedPlayer(nickname=data.nickname)
        logger.debug(PERMANENTLY_DISCONNECTED_PLAYER, disconnected_player=perm_disconnected_player.dict())
        sio.leave_room(disconnected_player.latest_sid, room=disconnected_player.room_id)
        await sio.emit(PERMANENTLY_DISCONNECTED_PLAYER, data=perm_disconnected_player.dict(), room=data.room_code)
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
