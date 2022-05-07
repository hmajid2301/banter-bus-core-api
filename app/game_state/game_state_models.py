from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from beanie import Document, Indexed
from pydantic.main import BaseModel


class UpdateQuestionRoundState(BaseModel):
    round_changed: bool
    new_round: Optional[str] = None


class DrawlossuemState(BaseModel):
    pass


class QuiblyState(BaseModel):
    pass


class PlayerScore(BaseModel):
    player_id: str
    score: int = 0


class FibbingItQuestion(BaseModel):
    fibber_question: str
    question: str
    answers: Optional[List[str]] = None


class NextQuestion(BaseModel):
    updated_round: UpdateQuestionRoundState
    next_question: Union[FibbingItQuestion, QuiblyState, DrawlossuemState, None]
    timer_in_seconds: int


class FibbingItRounds(BaseModel):
    opinion: List[FibbingItQuestion]
    likely: List[FibbingItQuestion]
    free_form: List[FibbingItQuestion]


class FibbingItAnswers(BaseModel):
    player_id: str
    answer: str


class FibbingItQuestionsState(BaseModel):
    rounds: FibbingItRounds
    question_nb: int = -1
    current_answers: List[FibbingItAnswers]


class FibbingItState(BaseModel):
    current_fibber_id: str
    questions_to_show: FibbingItQuestionsState
    current_round: str


class FibbingActions(Enum):
    show_question = "SHOW_QUESTION"
    submit_answers = "SUBMIT_ANSWERS"
    vote_on_fibber = "VOTE_ON_fibber"


class QuiblyActions(Enum):
    pass


class DrawlossuemActions(Enum):
    pass


class GamePaused(BaseModel):
    is_paused: bool = False
    paused_stopped_at: Optional[datetime] = None


class GameState(Document):
    room_id: Indexed(str, unique=True)  # type: ignore
    game_name: str
    player_scores: List[PlayerScore]
    state: Optional[Union[FibbingItState, QuiblyState, DrawlossuemState]] = None
    answers_expected_by_time: Optional[datetime] = None
    action: Union[FibbingActions, QuiblyActions, DrawlossuemActions]
    action_completed_by: Optional[datetime] = None
    paused: GamePaused

    class Collection:
        name = "game_state"
