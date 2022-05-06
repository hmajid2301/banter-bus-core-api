from typing import List, Tuple

from omnibus.log.logger import get_logger

from app.core.config import get_settings
from app.event_manager import error_handler, event_handler, leave_room
from app.exception_handlers import handle_error
from app.game_state.game_state_factory import get_game_state_service
from app.player.player_factory import get_player_service
from app.room.games.game import get_game
from app.room.room_events_models import (
    CreateRoom,
    EventResponse,
    GetNextQuestion,
    PermanentlyDisconnectedPlayer,
    PermanentlyDisconnectPlayer,
    RoomCreated,
)
from app.room.room_exceptions import RoomNotFound
from app.room.room_factory import get_room_service


@event_handler(input_model=CreateRoom)
@error_handler(Exception, handle_error)
async def create_room(sid: str, _: CreateRoom) -> Tuple[RoomCreated, None]:
    room_service = get_room_service()
    created_room = await room_service.create()
    room_created = RoomCreated(room_code=created_room.room_id)
    return room_created, None


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
        logger.exception("room not found", room_code=e.room_identifier)
        raise e


@event_handler(input_model=GetNextQuestion)
@error_handler(Exception, handle_error)
async def get_next_question(_: str, get_next_question: GetNextQuestion) -> Tuple[List[EventResponse], None]:
    game_state_service = get_game_state_service()
    game_state = await game_state_service.get_game_state_by_room_id(room_id=get_next_question.room_code)
    next_question = await game_state_service.get_next_question(game_state=game_state)

    player_service = get_player_service()
    players = await player_service.get_all_in_room(room_id=get_next_question.room_code)
    game = get_game(game_name=game_state.game_name)
    event_responses: List[EventResponse] = []
    for player in players:
        got_next_question = game.got_next_question(player=player, game_state=game_state, next_question=next_question)
        event_responses.append(EventResponse(send_to=player.latest_sid, response_data=got_next_question))
    return event_responses, None
