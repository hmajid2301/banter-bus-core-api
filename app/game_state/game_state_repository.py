import abc

from omnibus.database.repository import AbstractRepository
from pymongo.errors import DuplicateKeyError

from app.game_state.game_state_exceptions import (
    GameStateExistsException,
    GameStateNotFound,
)
from app.game_state.game_state_models import GameState


class AbstractGameStateRepository(AbstractRepository[GameState]):
    @abc.abstractmethod
    async def add(self, game_state: GameState):
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
