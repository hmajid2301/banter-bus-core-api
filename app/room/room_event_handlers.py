from typing import List, Tuple, Union

from omnibus.log.logger import get_logger
from pydantic import parse_obj_as

from app.core.config import get_settings
from app.event_manager import (
    enter_room,
    error_handler,
    event_handler,
    leave_room,
    publish_event,
)
from app.player.player_exceptions import PlayerHasNoRoomError, PlayerNotHostError
from app.player.player_factory import get_player_service
from app.player.player_models import NewPlayer, RoomPlayers
from app.room.room_events_models import (
    ERROR,
    NEW_ROOM_JOINED,
    CreateRoom,
    Error,
    GameStarted,
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
    StartGame,
)
from app.room.room_exceptions import (
    NicknameExistsException,
    RoomInInvalidState,
    RoomNotFound,
)
from app.room.room_factory import get_game_api, get_room_service


async def handle_error(sid):
    logger = get_logger()
    logger.exception("Failed action")
    error = Error(code="server_error", message="An unexpected error occurred on the server")
    await publish_event(event_name=ERROR, event_body=error, room=sid)


@event_handler(input_model=CreateRoom)
@error_handler(Exception, handle_error)
async def create_room(sid: str, _: CreateRoom) -> Tuple[RoomCreated, None]:
    room_service = get_room_service()
    created_room = await room_service.create()
    room_created = RoomCreated(room_code=created_room.room_id)
    return room_created, None


@event_handler(input_model=JoinRoom)
@error_handler(Exception, handle_error)
async def join_room(sid, data: JoinRoom) -> Tuple[Union[RoomJoined, Error], str]:
    logger = get_logger()
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
        await publish_event(event_name=NEW_ROOM_JOINED, event_body=new_room_joined, room=sid)
        return room_joined, sid
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="room_join_fail", message="room not found")
        return error, sid
    except NicknameExistsException as e:
        logger.exception("nickname already exists", room_code=data.room_code, nickname=e.nickname)
        error = Error(code="room_join_fail", message=f"nickname {e.nickname} already exists")
        return error, sid


@event_handler(input_model=RejoinRoom)
@error_handler(Exception, handle_error)
async def rejoin_room(sid, data: RejoinRoom) -> Tuple[Union[RoomJoined, Error], str]:
    logger = get_logger()
    try:
        room_service = get_room_service()
        player_service = get_player_service()
        room_players = await room_service.rejoin(
            player_service=player_service, player_id=data.player_id, latest_sid=sid
        )
        room_joined = await _publish_room_joined(sid, room_players.room_code, room_players)
        return room_joined, room_players.room_code
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="room_join_fail", message="room not found")
        return error, sid
    except PlayerHasNoRoomError:
        logger.exception("player has no room, they were likely disconnected from said room", player_id=data.player_id)
        error = Error(code="room_join_fail", message="disconnected from room, please re-join with a new nickname")
        return error, sid


async def _publish_room_joined(sid: str, room_code: str, room_players: RoomPlayers) -> RoomJoined:
    players = parse_obj_as(List[Player], room_players.players)
    room_joined = RoomJoined(players=players, host_player_nickname=room_players.host_player_nickname)
    enter_room(sid, room_code)
    return room_joined


@event_handler(input_model=KickPlayer)
@error_handler(Exception, handle_error)
async def kick_player(sid, data: KickPlayer) -> Tuple[Union[PlayerKicked, Error], str]:
    logger = get_logger()
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
        leave_room(kicked_player.latest_sid, room=data.room_code)
        return player_kicked, data.room_code
    except RoomInInvalidState as e:
        logger.exception("Game has started playing cannot kick players", room_state=e.room_state)
        error = Error(code="kick_player_fail", message="The game has started playing, so cannot kick player")
        return error, sid
    except PlayerNotHostError as e:
        logger.exception("player is not host so cannot kick", player_id=e.player_id, host_player_id=e.host_player_id)
        error = Error(code="kick_player_fail", message="You are not host, so cannot kick another player")
        return error, sid
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_idenitifer)
        error = Error(code="kick_player_fail", message="Room not found")
        return error, sid


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


@event_handler(input_model=StartGame)
@error_handler(Exception, handle_error)
async def start_game(_: str, data: StartGame) -> Tuple[GameStarted, str]:
    room_service = get_room_service()
    game_api = get_game_api()
    await room_service.start_game(
        game_api=game_api, game_name=data.game_name, player_id=data.player_id, room_id=data.room_code
    )

    game_started = GameStarted(game_name=data.game_name)
    return game_started, data.room_code
