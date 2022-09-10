from omnibus.log.logger import get_logger

from app.event_manager import error_handler, event_handler, leave_room, publish_event
from app.event_models import Error
from app.exception_handlers import handle_error
from app.player.player_exceptions import PlayerNotHostError
from app.player.player_models import NewPlayer
from app.room.lobby.lobby_event_helpers import enter_room_joined
from app.room.lobby.lobby_events_models import (
    NEW_ROOM_JOINED,
    CreateRoom,
    GameStarted,
    JoinRoom,
    KickPlayer,
    NewRoomJoined,
    PlayerKicked,
    RoomCreated,
    RoomJoined,
    StartGame,
)
from app.room.room_exceptions import (
    NicknameExistsException,
    RoomInInvalidState,
    RoomNotFound,
)
from app.room.room_factory import get_game_api, get_lobby_service


@error_handler(Exception, handle_error)
@event_handler(input_model=CreateRoom)
async def create_room(sid: str, _: CreateRoom) -> tuple[RoomCreated, None]:
    lobby_service = get_lobby_service()
    created_room = await lobby_service.create_room()
    room_created = RoomCreated(room_code=created_room.room_id)
    return room_created, None


@error_handler(Exception, handle_error)
@event_handler(input_model=JoinRoom)
async def join_room(sid, join_room: JoinRoom) -> tuple[RoomJoined | Error, str]:
    logger = get_logger()
    try:
        lobby_service = get_lobby_service()
        new_player = NewPlayer(
            avatar=join_room.avatar,  # type: ignore
            nickname=join_room.nickname,
            latest_sid=sid,
        )
        room_players = await lobby_service.join(room_id=join_room.room_code, new_player=new_player)
        room_joined = await enter_room_joined(sid, join_room.room_code, room_players)
        new_room_joined = NewRoomJoined(player_id=room_players.player_id)
        await publish_event(event_name=NEW_ROOM_JOINED, event_body=new_room_joined, room=sid)
        return room_joined, join_room.room_code
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.id)
        error = Error(code="room_join_fail", message="room not found")
        return error, sid
    except NicknameExistsException as e:
        logger.exception("nickname already exists", room_code=join_room.room_code, nickname=e.nickname)
        error = Error(code="room_join_fail", message=f"nickname {e.nickname} already exists")
        return error, sid


@error_handler(Exception, handle_error)
@event_handler(input_model=KickPlayer)
async def kick_player(sid, kick_player: KickPlayer) -> tuple[PlayerKicked | Error, str]:
    logger = get_logger()
    try:
        lobby_service = get_lobby_service()
        kicked_player = await lobby_service.kick_player(
            player_to_kick_nickname=kick_player.kick_player_nickname,
            player_attempting_kick=kick_player.player_id,
            room_id=kick_player.room_code,
        )
        player_kicked = PlayerKicked(nickname=kicked_player.nickname)
        leave_room(kicked_player.latest_sid, room=kick_player.room_code)
        return player_kicked, kick_player.room_code
    except RoomInInvalidState as e:
        logger.exception("Game has started playing cannot kick players", room_state=e.room_state)
        error = Error(code="kick_player_fail", message="The game has started playing, so cannot kick player")
        return error, sid
    except PlayerNotHostError as e:
        logger.exception("player is not host so cannot kick", player_id=e.player_id, host_player_id=e.host_player_id)
        error = Error(code="kick_player_fail", message="You are not host, so cannot kick another player")
        return error, sid
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.id)
        error = Error(code="kick_player_fail", message="Room not found")
        return error, sid


@error_handler(Exception, handle_error)
@event_handler(input_model=StartGame)
async def start_game(_: str, start_game: StartGame) -> tuple[GameStarted, str]:
    lobby_service = get_lobby_service()
    game_api = get_game_api()
    await lobby_service.start_game(
        game_api=game_api, game_name=start_game.game_name, player_id=start_game.player_id, room_id=start_game.room_code
    )

    game_started = GameStarted(game_name=start_game.game_name)
    return game_started, start_game.room_code
