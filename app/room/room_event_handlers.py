from omnibus.log.logger import get_logger

from app.core.config import get_settings
from app.event_manager import error_handler, event_handler, leave_room
from app.event_models import Error
from app.exception_handlers import handle_error
from app.game_state.game_state_exceptions import GameStateNotFound
from app.game_state.game_state_factory import get_game_state_service
from app.game_state.games.fibbing_it import FibbingIt
from app.player.player_exceptions import PlayerHasNoRoomError, PlayerNotInRoom
from app.player.player_factory import get_player_service
from app.room.games.game import get_game
from app.room.lobby.lobby_event_helpers import (
    get_next_question_helper,
    get_room_joined,
    send_unpause_event_if_no_players_are_disconnected,
)
from app.room.lobby.lobby_events_models import RoomJoined
from app.room.room_events_models import (
    AnswerSubmitted,
    EventResponse,
    GamePaused,
    GameUnpaused,
    GetNextQuestion,
    PauseGame,
    PermanentlyDisconnectedPlayer,
    PermanentlyDisconnectPlayer,
    RejoinRoom,
    SubmitAnswer,
    UnpauseGame,
)
from app.room.room_exceptions import RoomNotFound
from app.room.room_factory import get_lobby_service, get_room_service


@event_handler(input_model=PermanentlyDisconnectPlayer)
@error_handler(Exception, handle_error)
async def permanently_disconnect_player(
    _: str, data: PermanentlyDisconnectPlayer
) -> tuple[PermanentlyDisconnectedPlayer, str]:
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
        # TODO: remove from waiting for
        perm_disconnected_player = PermanentlyDisconnectedPlayer(nickname=data.nickname)
        return perm_disconnected_player, data.room_code
    except RoomNotFound as e:
        logger.exception("room not found", room_code=e.room_identifier)
        raise e


@event_handler(input_model=RejoinRoom)
@error_handler(Exception, handle_error)
async def rejoin_room(sid: str, rejoin_room: RejoinRoom) -> tuple[RoomJoined | Error, str]:
    logger = get_logger()
    try:
        lobby_service = get_lobby_service()
        room_players = await lobby_service.rejoin(player_id=rejoin_room.player_id, latest_sid=sid)

        room_service = get_room_service()
        room = await room_service.get(room_id=room_players.room_code)
        room_joined = await get_room_joined(sid, room_players.room_code, room_players)
        if room.state.is_room_rejoinable_and_started:
            await get_next_question_helper(sid=sid, player_id=rejoin_room.player_id, room_code=room_players.room_code)

        try:
            game_state_service = get_game_state_service()
            await send_unpause_event_if_no_players_are_disconnected(
                game_state_service=game_state_service, room_id=room_players.room_code, player_id=rejoin_room.player_id
            )
        except GameStateNotFound:
            pass

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


@event_handler(input_model=GetNextQuestion)
@error_handler(Exception, handle_error)
async def get_next_question(_: str, get_next_question: GetNextQuestion) -> tuple[list[EventResponse], None]:
    logger = get_logger()
    game_state_service = get_game_state_service()
    game_state = await game_state_service.get_game_state_by_room_id(room_id=get_next_question.room_code)
    next_question = await game_state_service.get_next_question(game_state=game_state)

    player_service = get_player_service()
    player = await player_service.get(player_id=get_next_question.player_id)
    if not player.room_id == get_next_question.room_code:
        logger.warning("Player getting next question not in room", get_next_question=get_next_question.dict())
        raise PlayerNotInRoom("player not in room, cannot get next question")

    players = await player_service.get_all_in_room(room_id=get_next_question.room_code)
    game = get_game(game_name=game_state.game_name)
    event_responses: list[EventResponse] = []
    for player in players:
        got_next_question = game.got_next_question(player=player, game_state=game_state, next_question=next_question)
        event_responses.append(EventResponse(send_to=player.latest_sid, response_data=got_next_question))
    return event_responses, None


@event_handler(input_model=PauseGame)
@error_handler(Exception, handle_error)
async def pause_game(_: str, pause_game: PauseGame) -> tuple[GamePaused, str]:
    room_service = get_room_service()
    game_state_service = get_game_state_service()
    paused_for_seconds = await room_service.pause_game(
        room_id=pause_game.room_code, player_id=pause_game.player_id, game_state_service=game_state_service
    )
    return GamePaused(paused_for=paused_for_seconds, message="Game paused by host."), pause_game.room_code


@event_handler(input_model=UnpauseGame)
@error_handler(Exception, handle_error)
async def unpause_game(_: str, unpause_game: UnpauseGame) -> tuple[GameUnpaused, str]:
    room_service = get_room_service()
    game_state_service = get_game_state_service()
    await room_service.unpause_game(
        room_id=unpause_game.room_code, player_id=unpause_game.player_id, game_state_service=game_state_service
    )
    return GameUnpaused(), unpause_game.room_code


@event_handler(input_model=SubmitAnswer)
@error_handler(Exception, handle_error)
async def submit_answer(sid: str, submit_answer: SubmitAnswer) -> tuple[AnswerSubmitted | Error, str]:
    game_state_service = get_game_state_service()
    player_service = get_player_service()
    player = await player_service.get(player_id=submit_answer.player_id)
    if not player.room_id == submit_answer.room_code:
        return Error(code="player_not_in_room", message="Player not in room"), sid

    players = await player_service.get_all_in_room(room_id=submit_answer.room_code)
    state = await game_state_service.get_game_state_by_room_id(room_id=submit_answer.room_code)

    fibbing_it = FibbingIt()
    player_ids = [player.player_id for player in players]
    new_state = fibbing_it.submit_answers(
        game_state=state, player_ids=player_ids, player_id=submit_answer.player_id, answer=submit_answer.answer
    )
    await game_state_service.update_state(game_state=state, state=new_state)
    return AnswerSubmitted(), sid
