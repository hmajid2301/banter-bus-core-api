from omnibus.log.logger import get_logger

from app.event_manager import error_handler, event_handler
from app.event_models import Error
from app.exception_handlers import handle_error
from app.game_state.game_state_exceptions import ActionTimedOut
from app.game_state.game_state_factory import get_game_state_service
from app.game_state.game_state_models import FibbingActions, FibbingItState
from app.game_state.games.fibbing_it.fibbing_it import FibbingIt
from app.player.player_factory import get_player_service
from app.room.room_events_models import (
    AnswerSubmittedFibbingIt,
    GetAnswersFibbingIt,
    GotAnswersFibbingIt,
    SubmitAnswerFibbingIt,
)


# TODO: check if all users have submitted answers, then move to next stage
@error_handler(Exception, handle_error)
@event_handler(input_model=SubmitAnswerFibbingIt)
async def submit_answer_fibbing_it(
    sid: str, submit_answer: SubmitAnswerFibbingIt
) -> tuple[AnswerSubmittedFibbingIt | Error, str]:
    logger = get_logger()
    game_state_service = get_game_state_service()
    player_service = get_player_service()
    player = await player_service.get(player_id=submit_answer.player_id)
    if player.room_id != submit_answer.room_code:
        return Error(code="player_not_in_room", message="Player not in room"), sid

    players = await player_service.get_all_in_room(room_id=submit_answer.room_code)
    state = await game_state_service.get_game_state_by_room_id(room_id=submit_answer.room_code)

    fibbing_it = FibbingIt()
    player_ids = [player.player_id for player in players]
    try:
        new_state = fibbing_it.submit_answers(
            game_state=state, player_ids=player_ids, player_id=submit_answer.player_id, answer=submit_answer.answer
        )

        await game_state_service.update_state(game_state=state, state=new_state)
        all_submitted = len(new_state.questions.current_answers) == len(players)
        return AnswerSubmittedFibbingIt(all_players_submitted=all_submitted), sid
    except ActionTimedOut as e:
        logger.exception("unable to submit answer, time has run out", now=e.now, completed_by=e.completed_by)
        return Error(code="time_run_out", message="Cannot submit answer, time has run out"), sid


@error_handler(Exception, handle_error)
@event_handler(input_model=GetAnswersFibbingIt)
async def get_answers_fibbing_it(sid: str, get_answers: GetAnswersFibbingIt) -> tuple[GotAnswersFibbingIt | Error, str]:
    logger = get_logger()
    logger.debug("Get all answers")
    game_state_service = get_game_state_service()
    player_service = get_player_service()
    player = await player_service.get(player_id=get_answers.player_id)
    if player.room_id != get_answers.room_code:
        return Error(code="player_not_in_room", message="Player not in room"), sid

    players = await player_service.get_all_in_room(room_id=get_answers.room_code)
    state = await game_state_service.get_game_state_by_room_id(room_id=get_answers.room_code)

    fibbing_it = FibbingIt()
    player_ids = [player.player_id for player in players]
    new_state = fibbing_it.select_random_answer(player_ids=player_ids, game_state=state)
    action = fibbing_it.get_next_action(current_action=state.action.value)
    await game_state_service.update_next_action(next_action=action, timer=300, game_state=state)
    answers = fibbing_it.get_player_answers(
        state=new_state, player_map={player.player_id: player.nickname for player in players}
    )
    timer = fibbing_it.get_timer(
        current_round=FibbingItState(**state.state.dict()).current_round,  # type: ignore
        action=FibbingActions(state.action),
    )
    return GotAnswersFibbingIt(answers=answers, timer_in_seconds=timer), sid
