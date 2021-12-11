import pytest
from fastapi import status
from httpx import AsyncClient

from app.question.question_models import Question
from app.question.question_repository import QuestionRepository
from tests.integration.data.question_test_data import (
    add_question_data,
    add_question_translation_data,
    disabled_question_data,
    enabled_question_data,
    get_question_data,
    get_question_groups_data,
    get_question_ids_data,
    get_question_translation_data,
    get_random_questions_data,
    remove_question_data,
    remove_question_translation_data,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, request_data, expected_status_code, expected_result",
    add_question_data,
    ids=[
        "add a quibly question",
        "add a drawlosseum question",
        "add a fibbing_it question",
        "try to add a question to a game that does not exist",
        "try to add a quibly question that already exists",
        "try to add a fibbing_it question that already exists",
        "try to add a drawlosseum question that already exists",
        "try to add an invalid drawlosseum question",
        "try to add an invalid fibbing_it question",
        "try to add an invalid quibly question",
        "try to add an invalid language code question",
    ],
)
async def test_add_question(
    client: AsyncClient, game_name: str, request_data: dict, expected_status_code: int, expected_result: dict
):
    url = f"/game/{game_name}/question"
    response = await client.post(url, json=request_data)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_201_CREATED:
        clean_response = _clean_response(response.json())
        assert clean_response == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, round_, language_code, limit, group_name, expected_status_code, expected_result_number",
    get_random_questions_data,
    ids=[
        "get some quibly questions for round pair",
        "get some quibly questions for round answer",
        "get some quibly questions for round",
        "get some quibly questions for round, limit 10",
        "get quibly_v3 groups (game not found)",
        "get quibly groups (invalid round < 0)",
        "get quibly groups (invalid round > 100)",
    ],
)
async def test_get_random_questions(
    client: AsyncClient,
    game_name: str,
    round_: str,
    language_code: str,
    limit: int,
    group_name: str,
    expected_status_code: int,
    expected_result_number: int,
):
    url = f"/game/{game_name}/question:random"
    response = await client.get(
        url, params={"limit": limit, "round": round_, "language_code": language_code, "group_name": group_name}
    )
    assert response.status_code == expected_status_code
    if response.status_code == status.HTTP_200_OK:
        random_questions = response.json()
        assert len(random_questions) == expected_result_number

        question_repository = QuestionRepository()
        for question in random_questions:
            existing_question = await question_repository.get(question_id=question["question_id"])
            assert existing_question.content[language_code] == question["content"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, round_, limit, expected_status_code, expected_result_number",
    get_question_groups_data,
    ids=[
        "get quibly, pair round groups",
        "get fibbing_it, opinion round groups",
        "get fibbing_it, free_form round groups",
        "get fibbing_it, likely round groups",
        "get drawlosseum, drawing round groups",
        "get quibly_v3 groups (game not found)",
        "get groups (round not found)",
        "get quibly groups (invalid round < 0)",
        "get quibly groups (invalid round > 100)",
    ],
)
async def test_get_random_question_groups(
    client: AsyncClient, game_name: str, round_: str, limit: int, expected_status_code: int, expected_result_number: int
):
    url = f"/game/{game_name}/question/group:random"
    response = await client.get(url, params={"limit": limit, "round": round_})
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        response_data = response.json()
        groups = response_data["groups"]
        assert len(groups) == expected_result_number

        question_repository = QuestionRepository()
        groups_in_db = await question_repository.get_groups(game_name=game_name, round_=round_)
        for group in groups:
            assert group in groups_in_db


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, cursor, limit, expected_status_code, expected_result",
    get_question_ids_data,
    ids=[
        "get 5 questions from fibbing_it",
        "get 5 questions from fibbing_it using cursor",
        "get all questions from drawlossuem",
        "get question ids (game not found)",
        "get question ids (invalid < 0 limit)",
        "get question ids (invalid > 100 limit)",
    ],
)
async def test_get_question_ids(
    client: AsyncClient,
    game_name: str,
    cursor: str,
    limit: int,
    expected_status_code: int,
    expected_result: dict,
):
    url = f"/game/{game_name}/question/id"
    response = await client.get(url, params={"cursor": cursor, "limit": limit})
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, expected_status_code, expected_result",
    get_question_data,
    ids=[
        "get a quibly question",
        "get a drawlosseum question",
        "get a fibbing_it question",
        "get a question which does not exist",
        "get a question where game does not exist",
    ],
)
async def test_get_question(
    client: AsyncClient, game_name: str, question_id: dict, expected_status_code: int, expected_result: dict
):
    url = f"/game/{game_name}/question/{question_id}"
    response = await client.get(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, expected_status_code",
    remove_question_data,
    ids=[
        "remove a quibly question",
        "remove a drawlosseum question",
        "remove a fibbing_it question",
        "remove a question which does not exist",
        "remove a question where game does not exist",
    ],
)
async def test_remove_question(client: AsyncClient, game_name: str, question_id: dict, expected_status_code: int):
    url = f"/game/{game_name}/question/{question_id}"
    response = await client.delete(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        question = await Question.find_one(Question.question_id == question_id)
        assert question is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, expected_status_code, expected_result",
    enabled_question_data,
    ids=[
        "enable a disabled question",
        "enable an enabled question",
        "try to enable question, id does not exist",
        "try to enable question, game does not exist",
    ],
)
async def test_enable_game(
    client: AsyncClient, game_name: str, question_id: str, expected_status_code: int, expected_result: dict
):
    url = f"/game/{game_name}/question/{question_id}:enable"
    response = await client.put(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, expected_status_code, expected_result",
    disabled_question_data,
    ids=[
        "disable an enabled question",
        "disable an disabled question",
        "try to disable question, id does not exist",
        "try to disable question, game does not exist",
    ],
)
async def test_disable_game(
    client: AsyncClient, game_name: str, question_id: str, expected_status_code: int, expected_result: dict
):
    url = f"/game/{game_name}/question/{question_id}:disable"
    response = await client.put(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, language_code, request_data, expected_status_code, expected_result",
    add_question_translation_data,
    ids=[
        "add a quibly question",
        "add a fibbing_it question",
        "add a drawlosseum question",
        "try to add a question (game not found)",
        "try to add a question (question not found)",
        "try to add a question (language code exists)",
        "try to add a question (invalid language code)",
    ],
)
async def test_add_question_translation(
    client: AsyncClient,
    game_name: str,
    question_id: str,
    language_code: str,
    request_data: str,
    expected_status_code: int,
    expected_result: dict,
):
    url = f"/game/{game_name}/question/{question_id}/{language_code}"
    response = await client.post(url, json=request_data)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_201_CREATED:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, language_code, expected_status_code, expected_result",
    get_question_translation_data,
    ids=[
        "get a quibly question",
        "get a fibbing_it question",
        "get a drawlosseum question",
        "try to get a question (game not found)",
        "try to get a question (question not found)",
        "try to get a question (invalid language code)",
    ],
)
async def test_get_question_translation(
    client: AsyncClient,
    game_name: str,
    question_id: str,
    language_code: str,
    expected_status_code: int,
    expected_result: dict,
):
    url = f"/game/{game_name}/question/{question_id}/{language_code}"
    response = await client.get(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, language_code, expected_status_code, expected_result",
    remove_question_translation_data,
    ids=[
        "remove a quibly question",
        "remove a fibbing_it question",
        "remove a drawlosseum question",
        "try to remove a question (game not found)",
        "try to remove a question (question not found)",
        "try to remove a question (invalid language code)",
    ],
)
async def test_remove_question_translation(
    client: AsyncClient,
    game_name: str,
    question_id: str,
    language_code: str,
    expected_status_code: int,
    expected_result: dict,
):
    url = f"/game/{game_name}/question/{question_id}/{language_code}"
    response = await client.delete(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        question = await Question.find_one(Question.question_id == question_id)
        assert question is not None
        question_dict = question.dict(by_alias=True, exclude_none=True)
        del question_dict["_id"]
        assert question_dict == expected_result


def _clean_response(response: dict):
    del response["question_id"]
    return response
