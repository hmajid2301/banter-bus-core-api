from datetime import datetime
from enum import Enum

from beanie import Document, Indexed
from pydantic.main import BaseModel


class UpdateQuestionRoundState(BaseModel):
    round_changed: bool
    new_round: str | None = None


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
    answers: list[str] | None = None


class NextQuestion(BaseModel):
    updated_round: UpdateQuestionRoundState
    next_question: FibbingItQuestion | QuiblyState | DrawlossuemState | None
    timer_in_seconds: int


class FibbingItRounds(BaseModel):
    opinion: list[FibbingItQuestion]
    likely: list[FibbingItQuestion]
    free_form: list[FibbingItQuestion]


class FibbingItQuestionsState(BaseModel):
    rounds: FibbingItRounds
    question_nb: int = -1
    current_answers: dict[str, str]


class FibbingItState(BaseModel):
    current_fibber_id: str
    questions: FibbingItQuestionsState
    current_round: str


class FibbingActions(Enum):
    show_question = "SHOW_QUESTION"
    submit_answers = "SUBMIT_ANSWERS"
    vote_on_fibber = "VOTE_ON_FIBBER"


class QuiblyActions(Enum):
    pass


class DrawlossuemActions(Enum):
    pass


class GamePaused(BaseModel):
    is_paused: bool = False
    paused_stopped_at: datetime | None = None
    waiting_for_players: list[str] = []


class GameState(Document):
    room_id: Indexed(str, unique=True)  # type: ignore
    game_name: str
    player_scores: list[PlayerScore]
    state: FibbingItState | QuiblyState | DrawlossuemState | None = None
    answers_expected_by_time: datetime | None = None
    action: FibbingActions | QuiblyActions | DrawlossuemActions
    action_completed_by: datetime | None = None
    paused: GamePaused

    class Collection:
        name = "game_state"
