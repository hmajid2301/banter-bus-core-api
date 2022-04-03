from typing import List, Optional, Union

from beanie import Document, Indexed
from pydantic.main import BaseModel


class DrawlossuemState(BaseModel):
    pass


class QuiblyState(BaseModel):
    pass


class PlayerScore(BaseModel):
    player_id: str
    score: int = 0


class FibbingItQuestion(BaseModel):
    faker_question: str
    question: str
    answers: Optional[List[str]] = None


class FibbingItRounds(BaseModel):
    opinion: List[FibbingItQuestion]
    likely: List[FibbingItQuestion]
    free_form: List[FibbingItQuestion]


class FibbingItAnswers(BaseModel):
    player_id: str
    answer: str


class FibbingItQuestionsState(BaseModel):
    rounds: FibbingItRounds
    question_nb: int = 0
    current_answers: List[FibbingItAnswers]


class FibbingItState(BaseModel):
    current_faker: str
    questions_to_show: FibbingItQuestionsState
    current_round: str


class GameState(Document):
    room_id: Indexed(str, unique=True)  # type: ignore
    game_name: str
    player_scores: List[PlayerScore]
    state: Optional[Union[FibbingItState, QuiblyState, DrawlossuemState]] = None

    class Collection:
        name = "game_state"
