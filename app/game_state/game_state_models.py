from typing import List, Union

from beanie import Document, Indexed
from pydantic.main import BaseModel


class DrawlossuemState(BaseModel):
    pass


class QuiblyState(BaseModel):
    pass


class FibbingItAnswers(BaseModel):
    player_id: str
    answer: str


class FibbingItFaker(BaseModel):
    faker_player_id: str
    fake_question: str


class FibbingItState(BaseModel):
    question: str
    faker: FibbingItFaker
    question_nb: int = 0
    round: str
    answers: FibbingItAnswers


class PlayerScore(BaseModel):
    player_id: str
    score: int


class GameState(Document):
    room_id: Indexed(str, unique=True)  # type: ignore
    game_name: str
    player: List[PlayerScore]
    state: Union[FibbingItState, QuiblyState, DrawlossuemState]

    class Collection:
        name = "game_state"
