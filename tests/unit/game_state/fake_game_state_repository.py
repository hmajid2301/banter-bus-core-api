from datetime import datetime, timedelta
from typing import List, Union

from app.game_state.game_state_exceptions import (
    GameStateExistsException,
    GameStateNotFound,
)
from app.game_state.game_state_models import (
    DrawlossuemActions,
    DrawlossuemState,
    FibbingActions,
    FibbingItState,
    GameState,
    QuiblyActions,
    QuiblyState,
)
from app.game_state.game_state_repository import AbstractGameStateRepository


class FakeGameStateRepository(AbstractGameStateRepository):
    def __init__(self, game_states: List[GameState]):
        self.game_states = game_states

    async def add(self, game_state: GameState):
        for existing_game_state in self.game_states:
            if existing_game_state.room_id == game_state.room_id:
                raise GameStateExistsException("game state already exists")

        self.game_states.append(game_state)

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def get(self, id_: str):
        for existing_game_state in self.game_states:
            if existing_game_state.room_id == id_:
                return existing_game_state

        raise GameStateNotFound("game state not found", room_identifier="room_id")

    async def update_state(
        self, game_state: GameState, state: Union[FibbingItState, QuiblyState, DrawlossuemState]
    ) -> GameState:
        game_state.state = state
        return game_state

    async def update_next_action(
        self,
        game_state: GameState,
        timer_in_seconds: int,
        next_action: Union[FibbingActions, QuiblyActions, DrawlossuemActions],
    ) -> GameState:
        game_state.next_action_completed_by = datetime.now() + timedelta(seconds=timer_in_seconds)
        game_state.next_action = next_action
        return game_state
