from omnibus.log.logger import get_logger

from app.core.config import get_settings
from app.event_manager import error_handler, event_handler, leave_room
from app.event_models import Error
from app.exception_handlers import handle_error
from app.game_state.game_state_factory import get_game_state_service
from app.player.player_exceptions import PlayerNotInRoom
from app.player.player_factory import get_player_service
from app.room.games.game import get_game
from app.room.lobby.lobby_event_helpers import (
    enter_room_joined,
    get_next_question_helper,
    send_unpause_event_if_no_players_are_disconnected,
)
from app.room.lobby.lobby_events_models import RoomJoined
from app.room.room_events_models import (
    EventResponse,
    GamePaused,
    GameUnpaused,
    GetNextQuestion,
    PauseGame,
    PermanentlyDisconnectedPlayer,
    PermanentlyDisconnectPlayer,
    RejoinRoom,
    UnpauseGame,
)
from app.room.room_exceptions import RoomNotFound
from app.room.room_factory import get_lobby_service, get_room_service


@error_handler(Exception, handle_error)
@event_handler(input_model=PermanentlyDisconnectPlayer)
async def permanently_disconnect_player(
    _: str, data: PermanentlyDisconnectPlayer
) -> tuple[PermanentlyDisconnectedPlayer, str]:
    logger = get_logger()

    try:
        config = get_settings()
        player_service = get_player_service()

        disconnected_player = await player_service.disconnect_player(
            nickname=data.nickname,
            room_id=data.room_code,
            disconnect_timer_in_seconds=config.DISCONNECT_TIMER_IN_SECONDS,
        )

        leave_room(disconnected_player.latest_sid, room=data.room_code)
        # TODO: remove from waiting for
        perm_disconnected_player = PermanentlyDisconnectedPlayer(nickname=data.nickname)
        return perm_disconnected_player, data.room_code
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.id)
        raise e


@error_handler(Exception, handle_error)
@event_handler(input_model=RejoinRoom)
async def rejoin_room(sid: str, rejoin_room: RejoinRoom) -> tuple[RoomJoined | Error, str]:
    logger = get_logger()
    try:
        lobby_service = get_lobby_service()
        room_players = await lobby_service.rejoin(player_id=rejoin_room.player_id, latest_sid=sid)

        room_service = get_room_service()
        room = await room_service.get(room_id=room_players.room_code)
        room_joined = await enter_room_joined(sid, room_players.room_code, room_players)
        if room.state.is_room_rejoinable_and_started:
            await get_next_question_helper(sid=sid, player_id=rejoin_room.player_id, room_code=room_players.room_code)

        game_state_service = get_game_state_service()
        await send_unpause_event_if_no_players_are_disconnected(
            game_state_service=game_state_service, room_id=room_players.room_code, player_id=rejoin_room.player_id
        )

        return room_joined, room_players.room_code
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.id)
        error = Error(code="room_join_fail", message="room not found")
        return error, sid


@error_handler(Exception, handle_error)
@event_handler(input_model=GetNextQuestion)
async def get_next_question(_: str, get_next_question: GetNextQuestion) -> tuple[list[EventResponse], None]:
    logger = get_logger()
    game_state_service = get_game_state_service()
    game_state = await game_state_service.get_game_state_by_room_id(room_id=get_next_question.room_code)
    next_question = await game_state_service.get_next_question(game_state=game_state)

    player_service = get_player_service()
    room_service = get_room_service()
    player = await player_service.get(player_id=get_next_question.player_id)
    room = await room_service.get(room_id=get_next_question.room_code)
    for player in room.players:
        if player.player_id == get_next_question.player_id:
            break
    else:
        logger.warning("Player getting next question not in room", get_next_question=get_next_question.dict())
        raise PlayerNotInRoom("player not in room, cannot get next question")

    players = room.players
    game = get_game(game_name=game_state.game_name)
    event_responses: list[EventResponse] = []
    for player in players:
        got_next_question = game.got_next_question(player=player, game_state=game_state, next_question=next_question)
        event_responses.append(EventResponse(send_to=player.latest_sid, response_data=got_next_question))
    return event_responses, None


@error_handler(Exception, handle_error)
@event_handler(input_model=PauseGame)
async def pause_game(_: str, pause_game: PauseGame) -> tuple[GamePaused, str]:
    room_service = get_room_service()
    game_state_service = get_game_state_service()
    paused_for_seconds = await room_service.pause_game(
        room_id=pause_game.room_code, player_id=pause_game.player_id, game_state_service=game_state_service
    )
    return GamePaused(paused_for=paused_for_seconds, message="Game paused by host."), pause_game.room_code


@error_handler(Exception, handle_error)
@event_handler(input_model=UnpauseGame)
async def unpause_game(_: str, unpause_game: UnpauseGame) -> tuple[GameUnpaused, str]:
    room_service = get_room_service()
    game_state_service = get_game_state_service()
    await room_service.unpause_game(
        room_id=unpause_game.room_code, player_id=unpause_game.player_id, game_state_service=game_state_service
    )
    return GameUnpaused(), unpause_game.room_code
