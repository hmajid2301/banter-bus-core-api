from typing import List

from pydantic.main import BaseModel


class DisconnectPlayers(BaseModel):
    disconnected_players: List[str]
