import abc
from datetime import datetime, timedelta
from typing import Union

from omnibus.database.repository import AbstractRepository
from pymongo.errors import DuplicateKeyError

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


class AbstractGameStateRepository(AbstractRepository[GameState]):
    @abc.abstractmethod
    async def update_state(
        self, game_state: GameState, state: Union[FibbingItState, QuiblyState, DrawlossuemState]
    ) -> GameState:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_next_action(
        self,
        game_state: GameState,
        timer_in_seconds: int,
        next_action: Union[FibbingActions, QuiblyActions, DrawlossuemActions],
    ) -> GameState:
        raise NotImplementedError


class GameStateRepository(AbstractGameStateRepository):
    async def add(self, game_state: GameState):
        try:
            await GameState.insert(game_state)
        except DuplicateKeyError:
            raise GameStateExistsException(f"game state {game_state.room_id=} already exists")

    async def remove(self, id_: str):
        return await super().remove(id_)

    async def get(self, id_: str) -> GameState:
        game_state = await GameState.find_one(GameState.room_id == id_)
        if game_state is None:
            raise GameStateNotFound(msg="game state not found", room_identifier=id_)
        return game_state

    async def update_state(
        self, game_state: GameState, state: Union[FibbingItState, QuiblyState, DrawlossuemState]
    ) -> GameState:
        game_state.state = state
        await game_state.save()
        return game_state

    async def update_next_action(
        self,
        game_state: GameState,
        timer_in_seconds: int,
        next_action: Union[FibbingActions, QuiblyActions, DrawlossuemActions],
    ) -> GameState:
        game_state.next_action_completed_by = datetime.now() + timedelta(seconds=timer_in_seconds)
        game_state.next_action = next_action
        await game_state.save()
        return game_state
