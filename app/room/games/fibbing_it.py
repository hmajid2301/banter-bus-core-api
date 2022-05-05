from app.game_state.game_state_models import (
    FibbingItQuestion,
    FibbingItState,
    GameState,
    NextQuestion,
    UpdateQuestionRoundState,
)
from app.player.player_models import Player
from app.room.games.abstract_game import AbstractGame
from app.room.games.exceptions import UnexpectedGameStateType
from app.room.room_events_models import GotNextQuestion, GotQuestionFibbingIt


class FibbingIt(AbstractGame):
    def got_next_question(self, player: Player, game_state: GameState, next_question: NextQuestion) -> GotNextQuestion:
        if not isinstance(game_state.state, FibbingItState):
            raise UnexpectedGameStateType("expected `game_state.state` to be of type `FibbingItState`")

        is_player_fibber = player.player_id == game_state.state.current_fibber_id
        got_next_question = self._get_got_next_question(is_player_fibber, next_question)
        return got_next_question

    @staticmethod
    def _get_got_next_question(is_player_fibber: bool, next_question: NextQuestion) -> GotNextQuestion:
        if not isinstance(next_question.next_question, FibbingItQuestion):
            raise UnexpectedGameStateType("expected `next_question.next_question` to be of type `FibbingItQuestion`")

        question = next_question.next_question.question
        if is_player_fibber:
            question = next_question.next_question.fibber_question

        got_next_question = GotNextQuestion(
            question=GotQuestionFibbingIt(
                is_fibber=is_player_fibber,
                question=question,
                answers=next_question.next_question.answers,
            ),
            updated_round=UpdateQuestionRoundState(**next_question.updated_round.dict()),
        )

        return got_next_question
