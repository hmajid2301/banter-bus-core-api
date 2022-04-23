import abc
from typing import List, Union

from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.game_state.game_state_models import (
    DrawlossuemActions,
    DrawlossuemState,
    FibbingActions,
    FibbingItQuestion,
    FibbingItState,
    QuiblyActions,
    QuiblyState,
)
from app.player.player_models import Player


class AbstractGame(abc.ABC):
    @abc.abstractmethod
    async def get_starting_state(
        self, question_client: AsyncQuestionsApi, players: List[Player]
    ) -> Union[FibbingItState, QuiblyState, DrawlossuemState]:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_question_state(
        self, current_state: Union[FibbingItState, QuiblyState, DrawlossuemState]
    ) -> Union[FibbingItState, QuiblyState, DrawlossuemState, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_next_question(
        self, current_state: Union[FibbingItState, QuiblyState, DrawlossuemState]
    ) -> Union[FibbingItQuestion, QuiblyState, DrawlossuemState, None]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_timer(
        self,
        current_state: Union[FibbingItState, QuiblyState, DrawlossuemState],
        prev_action: Union[FibbingActions, QuiblyActions, DrawlossuemActions],
    ) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def has_round_changed(
        self, current_state: Union[FibbingItState, QuiblyState, DrawlossuemState], old_round: str, new_round: str
    ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_next_action(self, current_action: str) -> Union[FibbingActions, QuiblyActions, DrawlossuemActions]:
        raise NotImplementedError
