from abc import ABC, abstractmethod

from pydantic import BaseModel

ERROR = "ERROR"


class EventModel(BaseModel, ABC):
    @property
    @abstractmethod
    def event_name(self) -> str:
        raise NotImplementedError


class Error(EventModel):
    code: str
    message: str

    @property
    def event_name(self):
        return ERROR
