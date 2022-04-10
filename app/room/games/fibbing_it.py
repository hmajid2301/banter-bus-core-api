from app.game_state.game_state_models import (
    FibbingItQuestion,
    FibbingItState,
    GameState,
    NextQuestion,
    UpdateQuestionRoundState,
)
from app.room.games.abstract_game import AbstractGame
from app.room.games.exceptions import UnexpectedGameStateType
from app.room.room_events_models import GotNextQuestion, GotQuestionFibbingIt


class FibbingIt(AbstractGame):
    def got_next_question(self, sid: str, game_state: GameState, next_question: NextQuestion) -> GotNextQuestion:
        if not isinstance(game_state.state, FibbingItState):
            raise UnexpectedGameStateType("expected `game_state.state` to be of type `FibbingItState`")
        if not isinstance(next_question.next_question, FibbingItQuestion):
            raise UnexpectedGameStateType("expected `next_question.next_question` to be of type `FibbingItQuestion`")

        is_faker = False
        question = next_question.next_question.question
        if sid == game_state.state.current_faker_sid:
            is_faker = True
            question = next_question.next_question.faker_question

        got_next_question = GotNextQuestion(
            question=GotQuestionFibbingIt(
                is_faker=is_faker,
                question=question,
                answers=next_question.next_question.answers,
            ),
            updated_round=UpdateQuestionRoundState(**next_question.updated_round.dict()),
        )
        return got_next_question
