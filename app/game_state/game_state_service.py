from typing import List

from pydantic import parse_obj_as

from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.game_state.exceptions import GameStateIsNoneError, InvalidGameAction
from app.game_state.game_state_exceptions import NoStateFound
from app.game_state.game_state_models import (
    FibbingActions,
    GameState,
    NextQuestion,
    PlayerScore,
    UpdateQuestionRoundState,
)
from app.game_state.game_state_repository import AbstractGameStateRepository
from app.game_state.games.abstract_game import AbstractGame
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
        game_state = GameState(
            game_name=game_name,
            room_id=room_id,
            player_scores=player_scores,
            state=state,
            next_action=FibbingActions.show_question,
        )
        await self.game_state_repository.add(game_state)
        return game_state

    async def get_next_question(self, game_state: GameState) -> NextQuestion:
        next_action = game_state.next_action
        if next_action != FibbingActions.show_question:
            raise InvalidGameAction(
                f"expected next action {FibbingActions.show_question.value} current next action {next_action}"
            )

        updated_round_state = await self._update_question_state(game_state=game_state)
        game = get_game(game_name=game_state.game_name)
        next_question = game.get_next_question(current_state=game_state.state)  # type: ignore
        timer = game.get_timer(current_state=game_state.state, prev_action=game_state.next_action)  # type: ignore
        game_state = await self._update_next_action(game=game, timer=timer, game_state=game_state)
        next_question_data = NextQuestion(
            updated_round=updated_round_state, next_question=next_question, timer_in_seconds=timer
        )
        return next_question_data

    async def _update_question_state(self, game_state: GameState) -> UpdateQuestionRoundState:
        old_round = game_state.state.current_round  # type: ignore
        game = get_game(game_name=game_state.game_name)

        updated_question_state = await game.update_question_state(current_state=game_state.state)  # type: ignore
        if updated_question_state is None:
            raise GameStateIsNoneError("expected question state to not be none")

        game_state = await self.game_state_repository.update_state(game_state=game_state, state=updated_question_state)

        new_round = updated_question_state.current_round  # type: ignore
        round_changed = game.has_round_changed(
            current_state=game_state.state,  # type: ignore
            old_round=old_round,
            new_round=new_round,
        )
        updated_round_state = UpdateQuestionRoundState(round_changed=round_changed, new_round=new_round)
        return updated_round_state

    async def _update_next_action(self, game: AbstractGame, timer: int, game_state: GameState) -> GameState:
        next_action = game.get_next_action(current_action=game_state.next_action.value)
        new_game_state = await self.game_state_repository.update_next_action(
            game_state=game_state, timer_in_seconds=timer, next_action=next_action
        )
        return new_game_state

    async def get_game_state_by_room_id(self, room_id) -> GameState:
        game_state = await self.game_state_repository.get(room_id)
        if game_state.state is None:
            raise NoStateFound(f"game state for {room_id=} is `None`")
        return game_state
