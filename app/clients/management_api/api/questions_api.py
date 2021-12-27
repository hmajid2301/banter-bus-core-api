# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable, List

from app.clients.management_api import models as m

if TYPE_CHECKING:
    from app.clients.management_api.api_client import ApiClient


class _QuestionsApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_add_question(self, game_name: str, question_in: m.QuestionIn) -> Awaitable[m.QuestionOut]:
        path_params = {"game_name": str(game_name)}

        body = question_in.dict()

        return self.api_client.request(
            type_=m.QuestionOut, method="POST", url="/game/{game_name}/question", path_params=path_params, json=body
        )

    def _build_for_add_question_translation(
        self, game_name: str, question_id: str, language_code: str, question_translation_in: m.QuestionTranslationIn
    ) -> Awaitable[m.QuestionOut]:
        path_params = {
            "game_name": str(game_name),
            "question_id": str(question_id),
            "language_code": str(language_code),
        }

        body = question_translation_in.dict()

        return self.api_client.request(
            type_=m.QuestionOut,
            method="POST",
            url="/game/{game_name}/question/{question_id}/{language_code}",
            path_params=path_params,
            json=body,
        )

    def _build_for_add_question_translation_0(
        self, game_name: str, question_id: str, language_code: str, question_translation_in: m.QuestionTranslationIn
    ) -> Awaitable[m.QuestionOut]:
        path_params = {
            "game_name": str(game_name),
            "question_id": str(question_id),
            "language_code": str(language_code),
        }

        body = question_translation_in.dict()

        return self.api_client.request(
            type_=m.QuestionOut,
            method="POST",
            url="/game/{game_name}/question/{question_id}/{language_code}",
            path_params=path_params,
            json=body,
        )

    def _build_for_disable_question(self, game_name: str, question_id: str) -> Awaitable[m.QuestionOut]:
        path_params = {"game_name": str(game_name), "question_id": str(question_id)}

        return self.api_client.request(
            type_=m.QuestionOut,
            method="PUT",
            url="/game/{game_name}/question/{question_id}:disable",
            path_params=path_params,
        )

    def _build_for_enable_question(self, game_name: str, question_id: str) -> Awaitable[m.QuestionOut]:
        path_params = {"game_name": str(game_name), "question_id": str(question_id)}

        return self.api_client.request(
            type_=m.QuestionOut,
            method="PUT",
            url="/game/{game_name}/question/{question_id}:enable",
            path_params=path_params,
        )

    def _build_for_get_question(self, game_name: str, question_id: str) -> Awaitable[m.QuestionOut]:
        path_params = {"game_name": str(game_name), "question_id": str(question_id)}

        return self.api_client.request(
            type_=m.QuestionOut,
            method="GET",
            url="/game/{game_name}/question/{question_id}",
            path_params=path_params,
        )

    def _build_for_get_question_ids(
        self, game_name: str, cursor: str, limit: int = None
    ) -> Awaitable[m.QuestionPaginationOut]:
        path_params = {"game_name": str(game_name)}

        query_params = {
            "cursor": str(cursor),
        }
        if limit is not None:
            query_params["limit"] = str(limit)

        return self.api_client.request(
            type_=m.QuestionPaginationOut,
            method="GET",
            url="/game/{game_name}/question/id",
            path_params=path_params,
            params=query_params,
        )

    def _build_for_get_question_translation(
        self, game_name: str, question_id: str, language_code: str
    ) -> Awaitable[m.QuestionTranslationOut]:
        path_params = {
            "game_name": str(game_name),
            "question_id": str(question_id),
            "language_code": str(language_code),
        }

        return self.api_client.request(
            type_=m.QuestionTranslationOut,
            method="GET",
            url="/game/{game_name}/question/{question_id}/{language_code}",
            path_params=path_params,
        )

    def _build_for_get_question_translation_0(
        self, game_name: str, question_id: str, language_code: str
    ) -> Awaitable[m.QuestionTranslationOut]:
        path_params = {
            "game_name": str(game_name),
            "question_id": str(question_id),
            "language_code": str(language_code),
        }

        return self.api_client.request(
            type_=m.QuestionTranslationOut,
            method="GET",
            url="/game/{game_name}/question/{question_id}/{language_code}",
            path_params=path_params,
        )

    def _build_for_get_random_groups(
        self, game_name: str, round: str = None, limit: int = None
    ) -> Awaitable[m.QuestionGroups]:
        path_params = {"game_name": str(game_name)}

        query_params = {}
        if round is not None:
            query_params["round"] = str(round)
        if limit is not None:
            query_params["limit"] = str(limit)

        return self.api_client.request(
            type_=m.QuestionGroups,
            method="GET",
            url="/game/{game_name}/question/group:random",
            path_params=path_params,
            params=query_params,
        )

    def _build_for_get_random_questions(
        self, game_name: str, round: str = None, language_code: str = None, group_name: str = None, limit: int = None
    ) -> Awaitable[List[m.QuestionSimpleOut]]:
        path_params = {"game_name": str(game_name)}

        query_params = {}
        if round is not None:
            query_params["round"] = str(round)
        if language_code is not None:
            query_params["language_code"] = str(language_code)
        if group_name is not None:
            query_params["group_name"] = str(group_name)
        if limit is not None:
            query_params["limit"] = str(limit)

        return self.api_client.request(
            type_=List[m.QuestionSimpleOut],
            method="GET",
            url="/game/{game_name}/question:random",
            path_params=path_params,
            params=query_params,
        )

    def _build_for_remove_question(self, game_name: str, question_id: str) -> Awaitable[m.Any]:
        path_params = {"game_name": str(game_name), "question_id": str(question_id)}

        return self.api_client.request(
            type_=m.Any,
            method="DELETE",
            url="/game/{game_name}/question/{question_id}",
            path_params=path_params,
        )

    def _build_for_remove_question_translation(
        self, game_name: str, question_id: str, language_code: str
    ) -> Awaitable[m.Any]:
        path_params = {
            "game_name": str(game_name),
            "question_id": str(question_id),
            "language_code": str(language_code),
        }

        return self.api_client.request(
            type_=m.Any,
            method="DELETE",
            url="/game/{game_name}/question/{question_id}/{language_code}",
            path_params=path_params,
        )

    def _build_for_remove_question_translation_0(
        self, game_name: str, question_id: str, language_code: str
    ) -> Awaitable[m.Any]:
        path_params = {
            "game_name": str(game_name),
            "question_id": str(question_id),
            "language_code": str(language_code),
        }

        return self.api_client.request(
            type_=m.Any,
            method="DELETE",
            url="/game/{game_name}/question/{question_id}/{language_code}",
            path_params=path_params,
        )


class AsyncQuestionsApi(_QuestionsApi):
    async def add_question(self, game_name: str, question_in: m.QuestionIn) -> m.QuestionOut:
        return await self._build_for_add_question(game_name=game_name, question_in=question_in)

    async def add_question_translation(
        self, game_name: str, question_id: str, language_code: str, question_translation_in: m.QuestionTranslationIn
    ) -> m.QuestionOut:
        return await self._build_for_add_question_translation(
            game_name=game_name,
            question_id=question_id,
            language_code=language_code,
            question_translation_in=question_translation_in,
        )

    async def add_question_translation_0(
        self, game_name: str, question_id: str, language_code: str, question_translation_in: m.QuestionTranslationIn
    ) -> m.QuestionOut:
        return await self._build_for_add_question_translation_0(
            game_name=game_name,
            question_id=question_id,
            language_code=language_code,
            question_translation_in=question_translation_in,
        )

    async def disable_question(self, game_name: str, question_id: str) -> m.QuestionOut:
        return await self._build_for_disable_question(game_name=game_name, question_id=question_id)

    async def enable_question(self, game_name: str, question_id: str) -> m.QuestionOut:
        return await self._build_for_enable_question(game_name=game_name, question_id=question_id)

    async def get_question(self, game_name: str, question_id: str) -> m.QuestionOut:
        return await self._build_for_get_question(game_name=game_name, question_id=question_id)

    async def get_question_ids(self, game_name: str, cursor: str, limit: int = None) -> m.QuestionPaginationOut:
        return await self._build_for_get_question_ids(game_name=game_name, cursor=cursor, limit=limit)

    async def get_question_translation(
        self, game_name: str, question_id: str, language_code: str
    ) -> m.QuestionTranslationOut:
        return await self._build_for_get_question_translation(
            game_name=game_name, question_id=question_id, language_code=language_code
        )

    async def get_question_translation_0(
        self, game_name: str, question_id: str, language_code: str
    ) -> m.QuestionTranslationOut:
        return await self._build_for_get_question_translation_0(
            game_name=game_name, question_id=question_id, language_code=language_code
        )

    async def get_random_groups(self, game_name: str, round: str = None, limit: int = None) -> m.QuestionGroups:
        return await self._build_for_get_random_groups(game_name=game_name, round=round, limit=limit)

    async def get_random_questions(
        self, game_name: str, round: str = None, language_code: str = None, group_name: str = None, limit: int = None
    ) -> List[m.QuestionSimpleOut]:
        return await self._build_for_get_random_questions(
            game_name=game_name, round=round, language_code=language_code, group_name=group_name, limit=limit
        )

    async def remove_question(self, game_name: str, question_id: str) -> m.Any:
        return await self._build_for_remove_question(game_name=game_name, question_id=question_id)

    async def remove_question_translation(self, game_name: str, question_id: str, language_code: str) -> m.Any:
        return await self._build_for_remove_question_translation(
            game_name=game_name, question_id=question_id, language_code=language_code
        )

    async def remove_question_translation_0(self, game_name: str, question_id: str, language_code: str) -> m.Any:
        return await self._build_for_remove_question_translation_0(
            game_name=game_name, question_id=question_id, language_code=language_code
        )


class SyncQuestionsApi(_QuestionsApi):
    def add_question(self, game_name: str, question_in: m.QuestionIn) -> m.QuestionOut:
        coroutine = self._build_for_add_question(game_name=game_name, question_in=question_in)
        return get_event_loop().run_until_complete(coroutine)

    def add_question_translation(
        self, game_name: str, question_id: str, language_code: str, question_translation_in: m.QuestionTranslationIn
    ) -> m.QuestionOut:
        coroutine = self._build_for_add_question_translation(
            game_name=game_name,
            question_id=question_id,
            language_code=language_code,
            question_translation_in=question_translation_in,
        )
        return get_event_loop().run_until_complete(coroutine)

    def add_question_translation_0(
        self, game_name: str, question_id: str, language_code: str, question_translation_in: m.QuestionTranslationIn
    ) -> m.QuestionOut:
        coroutine = self._build_for_add_question_translation_0(
            game_name=game_name,
            question_id=question_id,
            language_code=language_code,
            question_translation_in=question_translation_in,
        )
        return get_event_loop().run_until_complete(coroutine)

    def disable_question(self, game_name: str, question_id: str) -> m.QuestionOut:
        coroutine = self._build_for_disable_question(game_name=game_name, question_id=question_id)
        return get_event_loop().run_until_complete(coroutine)

    def enable_question(self, game_name: str, question_id: str) -> m.QuestionOut:
        coroutine = self._build_for_enable_question(game_name=game_name, question_id=question_id)
        return get_event_loop().run_until_complete(coroutine)

    def get_question(self, game_name: str, question_id: str) -> m.QuestionOut:
        coroutine = self._build_for_get_question(game_name=game_name, question_id=question_id)
        return get_event_loop().run_until_complete(coroutine)

    def get_question_ids(self, game_name: str, cursor: str, limit: int = None) -> m.QuestionPaginationOut:
        coroutine = self._build_for_get_question_ids(game_name=game_name, cursor=cursor, limit=limit)
        return get_event_loop().run_until_complete(coroutine)

    def get_question_translation(
        self, game_name: str, question_id: str, language_code: str
    ) -> m.QuestionTranslationOut:
        coroutine = self._build_for_get_question_translation(
            game_name=game_name, question_id=question_id, language_code=language_code
        )
        return get_event_loop().run_until_complete(coroutine)

    def get_question_translation_0(
        self, game_name: str, question_id: str, language_code: str
    ) -> m.QuestionTranslationOut:
        coroutine = self._build_for_get_question_translation_0(
            game_name=game_name, question_id=question_id, language_code=language_code
        )
        return get_event_loop().run_until_complete(coroutine)

    def get_random_groups(self, game_name: str, round: str = None, limit: int = None) -> m.QuestionGroups:
        coroutine = self._build_for_get_random_groups(game_name=game_name, round=round, limit=limit)
        return get_event_loop().run_until_complete(coroutine)

    def get_random_questions(
        self, game_name: str, round: str = None, language_code: str = None, group_name: str = None, limit: int = None
    ) -> List[m.QuestionSimpleOut]:
        coroutine = self._build_for_get_random_questions(
            game_name=game_name, round=round, language_code=language_code, group_name=group_name, limit=limit
        )
        return get_event_loop().run_until_complete(coroutine)

    def remove_question(self, game_name: str, question_id: str) -> m.Any:
        coroutine = self._build_for_remove_question(game_name=game_name, question_id=question_id)
        return get_event_loop().run_until_complete(coroutine)

    def remove_question_translation(self, game_name: str, question_id: str, language_code: str) -> m.Any:
        coroutine = self._build_for_remove_question_translation(
            game_name=game_name, question_id=question_id, language_code=language_code
        )
        return get_event_loop().run_until_complete(coroutine)

    def remove_question_translation_0(self, game_name: str, question_id: str, language_code: str) -> m.Any:
        coroutine = self._build_for_remove_question_translation_0(
            game_name=game_name, question_id=question_id, language_code=language_code
        )
        return get_event_loop().run_until_complete(coroutine)
