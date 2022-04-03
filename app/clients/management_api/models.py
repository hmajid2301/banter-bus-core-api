from enum import Enum
from typing import Any  # noqa
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CaertsianCoordinateColor(BaseModel):
    start: "DrawingPoint" = Field(..., alias="start")
    end: "DrawingPoint" = Field(..., alias="end")
    color: "str" = Field(..., alias="color")


class DrawingPoint(BaseModel):
    x: "float" = Field(..., alias="x")
    y: "float" = Field(..., alias="y")


class FibbingItAnswer(BaseModel):
    nickname: "str" = Field(..., alias="nickname")
    answer: "str" = Field(..., alias="answer")


class GameOut(BaseModel):
    name: "str" = Field(..., alias="name")
    display_name: "str" = Field(..., alias="display_name")
    description: "str" = Field(..., alias="description")
    enabled: "bool" = Field(..., alias="enabled")
    rules_url: "str" = Field(..., alias="rules_url")
    minimum_players: "int" = Field(..., alias="minimum_players")
    maximum_players: "int" = Field(..., alias="maximum_players")


class HTTPValidationError(BaseModel):
    detail: "Optional[List[ValidationError]]" = Field(None, alias="detail")


class QuestionGroup(BaseModel):
    name: "str" = Field(..., alias="name")
    type: "Optional[str]" = Field(None, alias="type")


class QuestionGroups(BaseModel):
    groups: "List[str]" = Field(..., alias="groups")


class QuestionIn(BaseModel):
    round: "Optional[str]" = Field(None, alias="round")
    content: "str" = Field(..., alias="content")
    language_code: "Optional[str]" = Field(None, alias="language_code")
    group: "Optional[QuestionGroup]" = Field(None, alias="group")


class QuestionOut(BaseModel):
    question_id: "str" = Field(..., alias="question_id")
    game_name: "str" = Field(..., alias="game_name")
    round: "Optional[str]" = Field(None, alias="round")
    enabled: "Optional[bool]" = Field(None, alias="enabled")
    content: "Dict[str, str]" = Field(..., alias="content")
    group: "Optional[QuestionGroup]" = Field(None, alias="group")


class QuestionPaginationOut(BaseModel):
    question_ids: "List[str]" = Field(..., alias="question_ids")
    cursor: "Optional[str]" = Field(None, alias="cursor")


class QuestionSimpleOut(BaseModel):
    question_id: "str" = Field(..., alias="question_id")
    content: "str" = Field(..., alias="content")
    type: "Optional[str]" = Field(None, alias="type")


class QuestionTranslationIn(BaseModel):
    content: "str" = Field(..., alias="content")


class QuestionTranslationOut(BaseModel):
    question_id: "str" = Field(..., alias="question_id")
    game_name: "str" = Field(..., alias="game_name")
    language_code: "str" = Field(..., alias="language_code")
    round: "Optional[str]" = Field(None, alias="round")
    enabled: "Optional[bool]" = Field(None, alias="enabled")
    content: "str" = Field(..., alias="content")
    group: "Optional[QuestionGroup]" = Field(None, alias="group")


class QuestionType(str, Enum):
    ANSWER = "answer"
    QUESTION = "question"


class QuiblyAnswer(BaseModel):
    nickname: "str" = Field(..., alias="nickname")
    answer: "str" = Field(..., alias="answer")
    votes: "int" = Field(..., alias="votes")


class StoryIn(BaseModel):
    game_name: "str" = Field(..., alias="game_name")
    question: "str" = Field(..., alias="question")
    round: "Optional[str]" = Field(None, alias="round")
    nickname: "Optional[str]" = Field(None, alias="nickname")
    answers: "Any" = Field(..., alias="answers")


class StoryOut(BaseModel):
    story_id: "str" = Field(..., alias="story_id")
    game_name: "str" = Field(..., alias="game_name")
    question: "str" = Field(..., alias="question")
    round: "Optional[str]" = Field(None, alias="round")
    nickname: "Optional[str]" = Field(None, alias="nickname")
    answers: "Any" = Field(..., alias="answers")


class ValidationError(BaseModel):
    loc: "List[str]" = Field(..., alias="loc")
    msg: "str" = Field(..., alias="msg")
    type: "str" = Field(..., alias="type")
