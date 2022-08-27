from datetime import datetime, timedelta

from pydantic import parse_obj_as

from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.game_state.game_state_exceptions import (
    GameIsPaused,
    GameStateAlreadyPaused,
    GameStateIsNoneError,
    GameStateNotPaused,
    InvalidGameAction,
    NoStateFound,
)
from app.game_state.game_state_models import (
    DrawlossuemActions,
    DrawlossuemState,
    FibbingActions,
    FibbingItState,
    GamePaused,
    GameState,
    NextQuestion,
    PlayerScore,
    QuiblyActions,
    QuiblyState,
    UpdateQuestionRoundState,
)
from app.game_state.game_state_repository import AbstractGameStateRepository
from app.game_state.games.game import get_game
from app.player.player_models import Player


class GameStateService:
    def __init__(self, game_state_repository: AbstractGameStateRepository, question_client: AsyncQuestionsApi) -> None:
        self.game_state_repository = game_state_repository
        self.question_client = question_client

    async def create(self, room_id: str, players: list[Player], game_name: str) -> GameState:
        game = get_game(game_name=game_name)
        state = await game.get_starting_state(players=players, question_client=self.question_client)
        player_scores = parse_obj_as(list[PlayerScore], players)
        game_state = GameState(
            game_name=game_name,
            room_id=room_id,
            player_scores=player_scores,
            state=state,
            action=FibbingActions.show_question,
            paused=GamePaused(),
        )
        await self.game_state_repository.add(game_state)
        return game_state

    # TODO: move to fibbing it
    # TODO: adjust actions so it changes at correct time
    async def get_next_question(self, game_state: GameState) -> NextQuestion:
        current_action = game_state.action
        now = datetime.now()
        if (
            game_state.paused.is_paused
            and game_state.paused.paused_stopped_at is not None
            and game_state.paused.paused_stopped_at < now
        ):
            raise GameIsPaused("game is paused unable to get next question")

        if current_action != FibbingActions.show_question:
            raise InvalidGameAction(
                f"expected next action {FibbingActions.show_question.value} current next action {current_action}"
            )

        updated_round_state = await self._update_question_state(game_state=game_state)
        game = get_game(game_name=game_state.game_name)
        next_question = game.get_next_question(current_state=game_state.state)  # type: ignore
        timer = game.get_timer(current_round=game_state.state.current_round, action=game_state.action)  # type: ignore
        next_action = game.get_next_action(current_action=game_state.action.value)
        game_state = await self.update_next_action(next_action=next_action, timer=timer, game_state=game_state)
        next_question_data = NextQuestion(
            updated_round=updated_round_state, next_question=next_question, timer_in_seconds=timer
        )
        return next_question_data

    async def update_state(
        self, game_state: GameState, state: FibbingItState | QuiblyState | DrawlossuemState
    ) -> GameState:
        game_state = await self.game_state_repository.update_state(game_state=game_state, state=state)
        return game_state

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

    async def update_next_action(
        self, next_action: FibbingActions | QuiblyActions | DrawlossuemActions, timer: int, game_state: GameState
    ) -> GameState:
        new_game_state = await self.game_state_repository.update_next_action(
            game_state=game_state, timer_in_seconds=timer, next_action=next_action
        )
        return new_game_state

    async def get_game_state_by_room_id(self, room_id) -> GameState:
        game_state = await self.game_state_repository.get(room_id)
        if game_state.state is None:
            raise NoStateFound(f"game state for {room_id=} is `None`")
        return game_state

    async def pause_game(self, room_id: str, player_disconnected: str | None = None) -> int:
        game_state = await self.game_state_repository.get(room_id)
        if game_state.paused.is_paused and not player_disconnected:
            raise GameStateAlreadyPaused("game is already paused")

        now = datetime.now()
        seconds_to_pause = 300
        paused_stopped_at = now + timedelta(seconds=300)

        waiting_for_players = self._add_waiting_for_players(game_state, player_disconnected)
        game_paused = GamePaused(
            is_paused=True, paused_stopped_at=paused_stopped_at, waiting_for_players=waiting_for_players
        )
        await self.game_state_repository.update_paused(game_state=game_state, game_paused=game_paused)
        return seconds_to_pause

    def _add_waiting_for_players(self, game_state: GameState, player_disconnected: str | None = None):
        waiting_for_players = game_state.paused.waiting_for_players
        if player_disconnected:
            if waiting_for_players:
                waiting_for_players.append(player_disconnected)
            else:
                waiting_for_players = [player_disconnected]
        return waiting_for_players

    async def unpause_game(self, room_id: str, player_reconnected: str | None = None) -> GamePaused:
        game_state = await self.game_state_repository.get(room_id)
        waiting_for_players = self._remove_waiting_for_players(game_state, player_reconnected)

        if not game_state.paused.is_paused:
            raise GameStateNotPaused("game is not paused")

        if waiting_for_players:
            game_state.paused.waiting_for_players = waiting_for_players
            game_paused = game_state.paused
        else:
            game_paused = GamePaused()
        await self.game_state_repository.update_paused(game_state=game_state, game_paused=game_paused)
        return game_paused

    def _remove_waiting_for_players(self, game_state: GameState, player_reconnected: str | None = None):
        waiting_for_players = game_state.paused.waiting_for_players

        if player_reconnected and waiting_for_players:
            waiting_for_players.remove(player_reconnected)
        else:
            waiting_for_players = []
        return waiting_for_players
