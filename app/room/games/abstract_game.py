import abc
from typing import List

from app.game_state.game_state_models import GameState, NextQuestion
from app.player.player_models import Player
from app.room.room_events_models import EventResponse


class AbstractGame(abc.ABC):
    @abc.abstractmethod
    def got_next_question(
        self, players: List[Player], game_state: GameState, next_question: NextQuestion
    ) -> List[EventResponse]:
        raise NotImplementedError
