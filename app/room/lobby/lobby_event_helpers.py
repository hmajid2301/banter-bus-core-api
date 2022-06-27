from pydantic import parse_obj_as

from app.event_manager import enter_room, publish_event
from app.game_state.game_state_factory import get_game_state_service
from app.game_state.game_state_service import GameStateService
from app.player.player_factory import get_player_service
from app.player.player_models import RoomPlayers
from app.room.games.game import get_game
from app.room.lobby.lobby_events_models import Player, RoomJoined
from app.room.room_events_models import GAME_UNPAUSED, GOT_NEXT_QUESTION, GameUnpaused


async def get_next_question_helper(sid: str, player_id: str, room_code: str):
    game_state_service = get_game_state_service()
    game_state = await game_state_service.get_game_state_by_room_id(room_id=room_code)
    next_question = await game_state_service.get_next_question(game_state=game_state)

    player_service = get_player_service()
    player = await player_service.get(player_id=player_id)
    game = get_game(game_name=game_state.game_name)
    got_next_question = game.got_next_question(player=player, game_state=game_state, next_question=next_question)
    await publish_event(event_name=GOT_NEXT_QUESTION, event_body=got_next_question, room=sid)


async def get_room_joined(sid: str, room_code: str, room_players: RoomPlayers) -> RoomJoined:
    players = parse_obj_as(list[Player], room_players.players)
    room_joined = RoomJoined(players=players, host_player_nickname=room_players.host_player_nickname)
    enter_room(sid, room_code)
    return room_joined


async def send_unpause_event_if_no_players_are_disconnected(
    player_id: str, room_id: str, game_state_service: GameStateService
):
    game_paused = await game_state_service.unpause_game(room_id=room_id, player_reconnected=player_id)
    if not game_paused.waiting_for_players:
        await publish_event(event_name=GAME_UNPAUSED, event_body=GameUnpaused(), room=room_id)
