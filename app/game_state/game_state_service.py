from typing import List, Union

from pydantic import parse_obj_as

from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.game_state.game_state_exceptions import NoStateFound
from app.game_state.game_state_models import (
    DrawlossuemState,
    FibbingItQuestion,
    GameState,
    PlayerScore,
    QuiblyState,
)
from app.game_state.game_state_repository import AbstractGameStateRepository
from app.game_state.games.game import get_game
from app.player.player_models import Player


class GameStateService:
    def __init__(self, game_state_repository: AbstractGameStateRepository, question_client: AsyncQuestionsApi) -> None:
        self.game_state_repository = game_state_repository
        self.question_client = question_client

    async def create(self, room_id: str, players: List[Player], game_name: str) -> GameState:
        game = get_game(game_name=game_name)
        state = await game.get_starting_state(players=players, question_client=self.question_client)
        player_scores = parse_obj_as(List[PlayerScore], players)
        game_state = GameState(game_name=game_name, room_id=room_id, player_scores=player_scores, state=state)
        await self.game_state_repository.add(game_state=game_state)
        return game_state

    async def get_next_question(self, room_id: str) -> Union[FibbingItQuestion, QuiblyState, DrawlossuemState, None]:
        game_state = await self.game_state_repository.get(room_id)
        game = get_game(game_name=game_state.game_name)
        if game_state.state is None:
            raise NoStateFound(f"game state for {room_id=} is `None`")
        next_question = await game.get_next_question(current_state=game_state.state)
        return next_question
