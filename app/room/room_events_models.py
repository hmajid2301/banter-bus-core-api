from pydantic import BaseModel, validator

from app.event_models import EventModel
from app.game_state.game_state_models import UpdateQuestionRoundState

REJOIN_ROOM = "REJOIN_ROOM"
PLAYER_DISCONNECTED = "PLAYER_DISCONNECTED"
HOST_DISCONNECTED = "HOST_DISCONNECTED"
PERMANENTLY_DISCONNECT_PLAYER = "PERMANENTLY_DISCONNECT_PLAYER"
PERMANENTLY_DISCONNECTED_PLAYER = "PERMANENTLY_DISCONNECTED_PLAYER"
GET_NEXT_QUESTION = "GET_NEXT_QUESTION"
GOT_NEXT_QUESTION = "GOT_NEXT_QUESTION"
PAUSE_GAME = "PAUSE_GAME"
GAME_PAUSED = "GAME_PAUSED"
UNPAUSE_GAME = "UNPAUSE_GAME"
GAME_UNPAUSED = "GAME_UNPAUSED"
SUBMIT_ANSWER = "SUBMIT_ANSWER"
ANSWER_SUBMITTED = "ANSWER_SUBMITTED"


class HostDisconnected(EventModel):
    new_host_nickname: str

    @property
    def event_name(self):
        return HOST_DISCONNECTED


class PlayerDisconnected(EventModel):
    nickname: str
    avatar: str | bytes

    @validator("avatar", pre=True)
    def base64_bytes_to_string(cls, value):
        if isinstance(value, bytes):
            return value.decode()
        return value

    @property
    def event_name(self):
        return PLAYER_DISCONNECTED


class RejoinRoom(EventModel):
    player_id: str

    @property
    def event_name(self):
        return REJOIN_ROOM


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
    player_id: str
    room_code: str

    @property
    def event_name(self):
        return GET_NEXT_QUESTION


class GotQuestionFibbingIt(BaseModel):
    is_fibber: bool
    question: str
    answers: list[str] | None = None


class GotQuestionDrawlossuem(BaseModel):
    pass


class GotQuestionQuibly(BaseModel):
    pass


class GotNextQuestion(EventModel):
    updated_round: UpdateQuestionRoundState
    question: GotQuestionFibbingIt | GotQuestionDrawlossuem | GotQuestionQuibly
    timer_in_seconds: int

    @property
    def event_name(self):
        return GOT_NEXT_QUESTION


class PauseGame(EventModel):
    player_id: str
    room_code: str

    @property
    def event_name(self):
        return PAUSE_GAME


class GamePaused(EventModel):
    paused_for: int
    message: str

    @property
    def event_name(self):
        return GAME_PAUSED


class UnpauseGame(EventModel):
    player_id: str
    room_code: str

    @property
    def event_name(self):
        return UNPAUSE_GAME


class GameUnpaused(EventModel):
    @property
    def event_name(self):
        return GAME_UNPAUSED


class SubmitAnswer(EventModel):
    player_id: str
    answer: str
    room_code: str

    @property
    def event_name(self):
        return SUBMIT_ANSWER


class AnswerSubmitted(EventModel):
    @property
    def event_name(self):
        return ANSWER_SUBMITTED


class EventResponse(BaseModel):
    send_to: str
    response_data: EventModel
