from typing import List

from fastapi import status
from httpx import Headers

from app.clients.management_api import models as m
from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.exceptions import UnexpectedResponse


class FakeGameAPI(AsyncGamesApi):
    def __init__(self, games: List[m.GameOut]):
        self.games = games

    async def get_game(self, game_name: str) -> m.GameOut:
        for game in self.games:
            if game.name == game_name:
                return game

        raise UnexpectedResponse(
            status_code=status.HTTP_404_NOT_FOUND, reason_phrase="", content="".encode("utf-8"), headers=Headers()
        )
