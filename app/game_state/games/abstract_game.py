import abc

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
        self, question_client: AsyncQuestionsApi, players: list[Player]
    ) -> FibbingItState | QuiblyState | DrawlossuemState:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_question_state(
        self, current_state: FibbingItState | QuiblyState | DrawlossuemState
    ) -> FibbingItState | QuiblyState | DrawlossuemState | None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_next_question(
        self, current_state: FibbingItState | QuiblyState | DrawlossuemState
    ) -> FibbingItQuestion | QuiblyState | DrawlossuemState | None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_timer(
        self,
        current_round: str,
        action: FibbingActions | QuiblyActions | DrawlossuemActions,
    ) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def has_round_changed(
        self, current_state: FibbingItState | QuiblyState | DrawlossuemState, old_round: str, new_round: str
    ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_next_action(self, current_action: str) -> FibbingActions | QuiblyActions | DrawlossuemActions:
        raise NotImplementedError
