import abc

from app.game_state.game_state_models import GameState, NextQuestion
from app.player.player_models import Player
from app.room.room_events_models import GotNextQuestion


class AbstractGame(abc.ABC):
    @abc.abstractmethod
    def got_next_question(self, player: Player, game_state: GameState, next_question: NextQuestion) -> GotNextQuestion:
        raise NotImplementedError
