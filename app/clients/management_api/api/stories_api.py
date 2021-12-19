# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable

from fastapi.encoders import jsonable_encoder

from app.clients.management_api import models as m

if TYPE_CHECKING:
    from app.clients.management_api.api_client import ApiClient


class _StoriesApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_add_story(self, story_in: m.StoryIn) -> Awaitable[m.StoryOut]:
        body = jsonable_encoder(story_in)

        return self.api_client.request(type_=m.StoryOut, method="POST", url="/story", json=body)

    def _build_for_get_story(self, story_id: str) -> Awaitable[m.StoryOut]:
        path_params = {"story_id": str(story_id)}

        return self.api_client.request(
            type_=m.StoryOut,
            method="GET",
            url="/story/{story_id}",
            path_params=path_params,
        )

    def _build_for_remove_story(self, story_id: str) -> Awaitable[m.Any]:
        path_params = {"story_id": str(story_id)}

        return self.api_client.request(
            type_=m.Any,
            method="DELETE",
            url="/story/{story_id}",
            path_params=path_params,
        )


class AsyncStoriesApi(_StoriesApi):
    async def add_story(self, story_in: m.StoryIn) -> m.StoryOut:
        return await self._build_for_add_story(story_in=story_in)

    async def get_story(self, story_id: str) -> m.StoryOut:
        return await self._build_for_get_story(story_id=story_id)

    async def remove_story(self, story_id: str) -> m.Any:
        return await self._build_for_remove_story(story_id=story_id)


class SyncStoriesApi(_StoriesApi):
    def add_story(self, story_in: m.StoryIn) -> m.StoryOut:
        coroutine = self._build_for_add_story(story_in=story_in)
        return get_event_loop().run_until_complete(coroutine)

    def get_story(self, story_id: str) -> m.StoryOut:
        coroutine = self._build_for_get_story(story_id=story_id)
        return get_event_loop().run_until_complete(coroutine)

    def remove_story(self, story_id: str) -> m.Any:
        coroutine = self._build_for_remove_story(story_id=story_id)
        return get_event_loop().run_until_complete(coroutine)
