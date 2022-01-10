# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable, List

from app.clients.management_api import models as m

if TYPE_CHECKING:
    from app.clients.management_api.api_client import ApiClient


class _GamesApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_disabled_game(self, game_name: str) -> Awaitable[m.GameOut]:
        path_params = {"game_name": str(game_name)}

        return self.api_client.request(
            type_=m.GameOut,
            method="PUT",
            url="/game/{game_name}:disable",
            path_params=path_params,
        )

    def _build_for_enable_game(self, game_name: str) -> Awaitable[m.GameOut]:
        path_params = {"game_name": str(game_name)}

        return self.api_client.request(
            type_=m.GameOut,
            method="PUT",
            url="/game/{game_name}:enable",
            path_params=path_params,
        )

    def _build_for_get_all_game_names(self, status: str = None) -> Awaitable[List[str]]:
        query_params = {}
        if status is not None:
            query_params["status"] = str(status)

        return self.api_client.request(
            type_=List[str],
            method="GET",
            url="/game",
            params=query_params,
        )

    def _build_for_get_game(self, game_name: str) -> Awaitable[m.GameOut]:
        path_params = {"game_name": str(game_name)}

        return self.api_client.request(
            type_=m.GameOut,
            method="GET",
            url="/game/{game_name}",
            path_params=path_params,
        )


class AsyncGamesApi(_GamesApi):
    async def disabled_game(self, game_name: str) -> m.GameOut:
        return await self._build_for_disabled_game(game_name=game_name)

    async def enable_game(self, game_name: str) -> m.GameOut:
        return await self._build_for_enable_game(game_name=game_name)

    async def get_all_game_names(self, status: str = None) -> List[str]:
        return await self._build_for_get_all_game_names(status=status)

    async def get_game(self, game_name: str) -> m.GameOut:
        return await self._build_for_get_game(game_name=game_name)


class SyncGamesApi(_GamesApi):
    def disabled_game(self, game_name: str) -> m.GameOut:
        coroutine = self._build_for_disabled_game(game_name=game_name)
        return get_event_loop().run_until_complete(coroutine)

    def enable_game(self, game_name: str) -> m.GameOut:
        coroutine = self._build_for_enable_game(game_name=game_name)
        return get_event_loop().run_until_complete(coroutine)

    def get_all_game_names(self, status: str = None) -> List[str]:
        coroutine = self._build_for_get_all_game_names(status=status)
        return get_event_loop().run_until_complete(coroutine)

    def get_game(self, game_name: str) -> m.GameOut:
        coroutine = self._build_for_get_game(game_name=game_name)
        return get_event_loop().run_until_complete(coroutine)
