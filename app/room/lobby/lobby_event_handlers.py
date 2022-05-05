from typing import List, Tuple, Union

from omnibus.log.logger import get_logger
from pydantic import parse_obj_as

from app.event_manager import (
    enter_room,
    error_handler,
    event_handler,
    leave_room,
    publish_event,
)
from app.event_models import Error
from app.exception_handlers import handle_error
from app.game_state.game_state_factory import get_game_state_service
from app.player.player_exceptions import PlayerHasNoRoomError, PlayerNotHostError
from app.player.player_factory import get_player_service
from app.player.player_models import NewPlayer, RoomPlayers
from app.room.games.game import get_game
from app.room.lobby.lobby_events_models import (
    NEW_ROOM_JOINED,
    GameStarted,
    JoinRoom,
    KickPlayer,
    NewRoomJoined,
    Player,
    PlayerKicked,
    RejoinRoom,
    RoomJoined,
    StartGame,
)
from app.room.room_events_models import GOT_NEXT_QUESTION
from app.room.room_exceptions import (
    NicknameExistsException,
    RoomInInvalidState,
    RoomNotFound,
)
from app.room.room_factory import get_game_api, get_lobby_service, get_room_service


@event_handler(input_model=JoinRoom)
@error_handler(Exception, handle_error)
async def join_room(sid, join_room: JoinRoom) -> Tuple[Union[RoomJoined, Error], str]:
    logger = get_logger()
    try:
        lobby_service = get_lobby_service()
        new_player = NewPlayer(
            avatar=join_room.avatar,  # type: ignore
            nickname=join_room.nickname,
            latest_sid=sid,
        )
        room_players = await lobby_service.join(room_id=join_room.room_code, new_player=new_player)
        room_joined = await _publish_room_joined(sid, join_room.room_code, room_players)
        new_room_joined = NewRoomJoined(player_id=room_players.player_id)
        await publish_event(event_name=NEW_ROOM_JOINED, event_body=new_room_joined, room=sid)
        return room_joined, join_room.room_code
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_identifier)
        error = Error(code="room_join_fail", message="room not found")
        return error, sid
    except NicknameExistsException as e:
        logger.exception("nickname already exists", room_code=join_room.room_code, nickname=e.nickname)
        error = Error(code="room_join_fail", message=f"nickname {e.nickname} already exists")
        return error, sid


@event_handler(input_model=RejoinRoom)
@error_handler(Exception, handle_error)
async def rejoin_room(sid: str, rejoin_room: RejoinRoom) -> Tuple[Union[RoomJoined, Error], str]:
    logger = get_logger()
    try:
        lobby_service = get_lobby_service()
        room_players = await lobby_service.rejoin(player_id=rejoin_room.player_id, latest_sid=sid)

        room_service = get_room_service()
        room = await room_service.get(room_id=room_players.room_code)
        room_joined = await _publish_room_joined(sid, room_players.room_code, room_players)
        if room.state.is_room_rejoinable_and_started:
            await _get_next_question(sid=sid, player_id=rejoin_room.player_id, room_code=room_players.room_code)
        return room_joined, room_players.room_code
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_identifier)
        error = Error(code="room_join_fail", message="room not found")
        return error, sid
    except PlayerHasNoRoomError:
        logger.exception(
            "player has no room, they were likely disconnected from said room", player_id=rejoin_room.player_id
        )
        error = Error(code="room_join_fail", message="disconnected from room, please re-join with a new nickname")
        return error, sid


async def _get_next_question(sid: str, player_id: str, room_code: str):
    game_state_service = get_game_state_service()
    game_state = await game_state_service.get_game_state_by_room_id(room_id=room_code)
    next_question = await game_state_service.get_next_question(game_state=game_state)

    player_service = get_player_service()
    player = await player_service.get(player_id=player_id)
    game = get_game(game_name=game_state.game_name)
    got_next_question = game.got_next_question(player=player, game_state=game_state, next_question=next_question)
    await publish_event(event_name=GOT_NEXT_QUESTION, event_body=got_next_question, room=sid)


async def _publish_room_joined(sid: str, room_code: str, room_players: RoomPlayers) -> RoomJoined:
    players = parse_obj_as(List[Player], room_players.players)
    room_joined = RoomJoined(players=players, host_player_nickname=room_players.host_player_nickname)
    enter_room(sid, room_code)
    return room_joined


@event_handler(input_model=KickPlayer)
@error_handler(Exception, handle_error)
async def kick_player(sid, kick_player: KickPlayer) -> Tuple[Union[PlayerKicked, Error], str]:
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
        logger.exception("room not found", room_code=e.room_identifier)
        error = Error(code="kick_player_fail", message="Room not found")
        return error, sid


@event_handler(input_model=StartGame)
@error_handler(Exception, handle_error)
async def start_game(_: str, start_game: StartGame) -> Tuple[GameStarted, str]:
    lobby_service = get_lobby_service()
    game_api = get_game_api()
    await lobby_service.start_game(
        game_api=game_api, game_name=start_game.game_name, player_id=start_game.player_id, room_id=start_game.room_code
    )

    game_started = GameStarted(game_name=start_game.game_name)
    return game_started, start_game.room_code
