from typing import List, Optional, Union

from pydantic import BaseModel

from app.event_models import EventModel
from app.game_state.game_state_models import UpdateQuestionRoundState

CREATE_ROOM = "CREATE_ROOM"
ROOM_CREATED = "ROOM_CREATED"
PERMANENTLY_DISCONNECT_PLAYER = "PERMANENTLY_DISCONNECT_PLAYER"
PERMANENTLY_DISCONNECTED_PLAYER = "PERMANENTLY_DISCONNECTED_PLAYER"
GET_NEXT_QUESTION = "GET_NEXT_QUESTION"
GOT_NEXT_QUESTION = "GOT_NEXT_QUESTION"


class CreateRoom(EventModel):
    @property
    def event_name(self):
        return CREATE_ROOM


class RoomCreated(EventModel):
    room_code: str

    @property
    def event_name(self):
        return ROOM_CREATED


class PermanentlyDisconnectPlayer(EventModel):
    nickname: str
    room_code: str

    @property
    def event_name(self):
        return PERMANENTLY_DISCONNECT_PLAYER


class PermanentlyDisconnectedPlayer(EventModel):
    nickname: str

    @property
    def event_name(self):
        return PERMANENTLY_DISCONNECTED_PLAYER


class GetNextQuestion(EventModel):
    room_code: str

    @property
    def event_name(self):
        return GET_NEXT_QUESTION


class GotQuestionFibbingIt(BaseModel):
    is_fibber: bool
    question: str
    answers: Optional[List[str]] = None


class GotQuestionDrawlossuem(BaseModel):
    pass


class GotQuestionQuibly(BaseModel):
    pass


class GotNextQuestion(EventModel):
    updated_round: UpdateQuestionRoundState
    question: Union[GotQuestionFibbingIt, GotQuestionDrawlossuem, GotQuestionQuibly]

    @property
    def event_name(self):
        return GOT_NEXT_QUESTION


class EventResponse(BaseModel):
    send_to: str
    response: EventModel
