# flake8: noqa E501
from asyncio import get_event_loop
from collections.abc import Awaitable
from typing import TYPE_CHECKING

from app.clients.management_api import models as m

if TYPE_CHECKING:
    from app.clients.management_api.api_client import ApiClient


class _DefaultApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_endpoint(
        self,
    ) -> Awaitable[m.Any]:
        return self.api_client.request(
            type_=m.Any,
            method="GET",
            url="/health",
        )


class AsyncDefaultApi(_DefaultApi):
    async def endpoint(
        self,
    ) -> m.Any:
        return await self._build_for_endpoint()


class SyncDefaultApi(_DefaultApi):
    def endpoint(
        self,
    ) -> m.Any:
        coroutine = self._build_for_endpoint()
        return get_event_loop().run_until_complete(coroutine)
