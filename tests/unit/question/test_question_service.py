import copy
import uuid
from typing import List

import pytest
from pytest_mock import MockFixture

from app.game.game_exceptions import GameNotFound
from app.question.question_exceptions import QuestionNotFound
from app.question.question_models import Question
from app.question.question_service import QuestionService
from tests.unit.question.fake_question_repository import FakeQuestionRepository
from tests.unit.question.question_service_data import (
    add_question_data,
    add_question_data_fail,
    get_groups_data,
    get_groups_data_fail,
    get_question_data,
    get_question_ids_data,
    get_question_ids_data_fail,
    get_random_questions_data,
    get_random_questions_data_fail,
    update_enabled_status_question_data,
)


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.fixture()
def questions() -> List[Question]:
    from tests.data.question_collection import questions

    return copy.deepcopy(questions)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question_dict, expected_result",
    add_question_data,
    ids=[
        "add a quibly question, round pair",
        "add a quibly question, round answer and language_code de",
        "add a quibly question, round group",
        "add a drawlosseum question",
        "add a fibbing_it question, round opinion and group bike question, language_code en",
        "add a fibbing_it question, round opinion and group bike answer",
        "add a fibbing_it question, round free_form and group horse",
        "add a fibbing_it question, round likely",
    ],
)
async def test_add_question(question_dict: dict, expected_result: dict, mocker: MockFixture):
    question_repository = FakeQuestionRepository(questions=[])
    question_service = QuestionService(question_repository=question_repository)

    mock_uuid = mocker.patch.object(uuid, "uuid4", autospec=True)
    mock_uuid.return_value = uuid.UUID(hex="5ecd5827b6ef4067b5ac3ceac07dde9f")

    new_question = await question_service.add(question_dict=question_dict)
    assert expected_result == new_question.dict(exclude_none=True, by_alias=True)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question_dict, expected_exception",
    add_question_data_fail,
    ids=[
        "try to add a quibly question, invalid round",
        "try to add a quibly question, missing round",
        "try to add a drawlosseum question, missing content",
        "try to add a fibbing_it question, invalid round",
        "try to add a fibbing_it question, round opinion, invalid type",
        "try to add a fibbing_it question, round opinion, missing group ",
        "try to add a fibbing_it question, invalid language code",
        "try to add a fibbing_it_v3 question game does not exist",
        "try to add a quibly question round pair already exists",
        "try to add a quibly question round answers, language de already exists",
        "try to add a quibly question round group, language code fr already exists",
        "try to add a fibbing_it question round opinions already exists",
        "try to add a fibbing_it question round free_form already exists",
        "try to add a fibbing_it question round likely already exists",
        "try to add a drawlosseum question already exists",
    ],
)
async def test_add_question_fail(question_dict: dict, expected_exception, questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(expected_exception):
        await question_service.add(question_dict=question_dict)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, round_, language_code, limit, group_name, expected_result_num",
    get_random_questions_data,
    ids=[
        "get some quibly questions for round pair",
        "get some quibly questions for round answer",
        "get some quibly questions for round group",
        "get some quibly questions for round group, limit 10",
        "get some quibly questions for round group, language ur",
        "get some fibbing_it questions for round opinion, horse_group group",
        "get some fibbing_it questions for round free_form, bike_group group",
        "get some fibbing_it questions for round likely",
        "get some drawlosseum questions",
    ],
)
async def test_get_random_questions(
    game_name: str,
    round_: str,
    language_code: str,
    limit: int,
    group_name: str,
    expected_result_num: int,
    questions: List[Question],
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    random_questions = await question_service.get_random(
        game_name=game_name,
        round_=round_,
        language_code=language_code,
        limit=limit,
        group_name=group_name,
    )
    assert len(random_questions) == expected_result_num
    for question in random_questions:
        existing_question = await question_repository.get(question_id=question.question_id)
        assert existing_question.content[language_code] == question.content


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, round_, language_code, limit, group_name, expected_exception",
    get_random_questions_data_fail,
    ids=[
        "get random question, game not found",
        "get random question, invalid limit",
    ],
)
async def test_get_random_questions_fail(
    game_name: str,
    round_: str,
    language_code: str,
    limit: int,
    group_name: str,
    expected_exception,
    questions: List[Question],
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(expected_exception):
        await question_service.get_random(
            game_name=game_name,
            round_=round_,
            language_code=language_code,
            limit=limit,
            group_name=group_name,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, round_, limit",
    get_groups_data,
    ids=[
        "get quibly groups",
        "get fibbing_it round opinion group",
        "get fibbing_it round free_form groups",
        "get fibbing_it round likely groups",
        "get drawlossuem groups",
    ],
)
async def test_get_groups(game_name: str, round_: str, limit: int, questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)
    expected_groups = await question_repository.get_groups(game_name=game_name, round_=round_)

    random_groups = await question_service.get_random_groups(game_name=game_name, round_=round_, limit=limit)

    if expected_groups:
        assert len(random_groups) == limit
    else:
        assert len(random_groups) == 0

    for group in random_groups:
        assert group in expected_groups


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, round_, limit, expected_exception",
    get_groups_data_fail,
    ids=[
        "get groups, game not found",
        "get groups, round not found",
        "get groups, invalid limit",
    ],
)
async def test_get_groups_fail(game_name: str, round_: str, limit: int, expected_exception, questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(expected_exception):
        await question_service.get_random_groups(game_name=game_name, round_=round_, limit=limit)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, cursor, limit, expected_result",
    get_question_ids_data,
    ids=[
        "get 5 questions from fibbing_it",
        "get 5 questions from fibbing_it using cursor",
        "get all questions from drawlossuem",
        "get 2 questions from quibly",
        "get questions from quibly using cursor",
    ],
)
async def test_get_question_ids(
    game_name: str, cursor: str, limit: int, expected_result: dict, questions: List[Question]
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question_ids = await question_service.get_ids(game_name=game_name, cursor=cursor, limit=limit)
    assert question_ids.dict(exclude_none=True) == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, cursor, limit, expected_exception",
    get_question_ids_data_fail,
    ids=[
        "get question ids (game not found)",
        "get question ids (invalid limit)",
    ],
)
async def test_get_question_ids_fail(
    game_name: str, cursor: str, limit: int, expected_exception, questions: List[Question]
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(expected_exception):
        await question_service.get_ids(game_name=game_name, cursor=cursor, limit=limit)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question_id, game_name, expected_question",
    get_question_data,
    ids=[
        "get a quibly question",
        "get a fibbing_it question",
        "get a drawlosseum question",
    ],
)
async def test_get_question(
    question_id: str,
    game_name: str,
    expected_question: dict,
    questions: List[Question],
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question = await question_service.get(question_id=question_id, game_name=game_name)
    assert question.dict(by_alias=True, exclude_none=True) == expected_question


@pytest.mark.asyncio
async def test_get_question_does_not_exist():
    question_repository = FakeQuestionRepository(questions=[])
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(QuestionNotFound):
        await question_service.get(question_id="a-random-id", game_name="quibly")


@pytest.mark.asyncio
async def test_get_question_game_does_not_exist(questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(GameNotFound):
        await question_service.get(question_id="101464a5-337f-4ce7-a4df-2b00764e5d8d", game_name="quibly_v3")


@pytest.mark.asyncio
async def test_remove_question(questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question_id = "101464a5-337f-4ce7-a4df-2b00764e5d8d"
    await question_service.remove(question_id=question_id, game_name="quibly")
    with pytest.raises(QuestionNotFound):
        await question_repository.get(question_id=question_id)


@pytest.mark.asyncio
async def test_remove_question_does_not_exist(questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question_id = "a-random_id"
    with pytest.raises(QuestionNotFound):
        await question_service.remove(question_id=question_id, game_name="quibly")


@pytest.mark.asyncio
async def test_remove_question_game_does_not_exist(questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question_id = "101464a5-337f-4ce7-a4df-2b00764e5d8d"
    with pytest.raises(GameNotFound):
        await question_service.remove(question_id=question_id, game_name="quibly_v3")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id",
    update_enabled_status_question_data,
    ids=[
        "enable disabled game",
        "enable enabled game",
    ],
)
async def test_enable_question(game_name: str, question_id: str, questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question = await question_service.update_enabled_status(game_name=game_name, question_id=question_id, enabled=True)
    assert question.enabled is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id",
    update_enabled_status_question_data,
    ids=[
        "disable disabled game",
        "disable enabled game",
    ],
)
async def test_disable_question(game_name: str, question_id: str, questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question = await question_service.update_enabled_status(game_name=game_name, question_id=question_id, enabled=False)
    assert question.enabled is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "enabled_status",
    [True, False],
    ids=[
        "try to enable game (game not found)",
        "try to disable game (game not found)",
    ],
)
async def test_update_enable_status_question_does_not_exist(enabled_status: bool, questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question_id = "a-random_id"
    with pytest.raises(QuestionNotFound):
        await question_service.update_enabled_status(
            game_name="quibly", question_id=question_id, enabled=enabled_status
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "enabled_status",
    [True, False],
    ids=[
        "try to enable game (game not found)",
        "try to disable game (game not found)",
    ],
)
async def test_update_enable_state_question_game_does_not_exist(enabled_status: bool, questions: List[Question]):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    question_id = "101464a5-337f-4ce7-a4df-2b00764e5d8d"
    with pytest.raises(GameNotFound):
        await question_service.update_enabled_status(
            game_name="quibly_v3", question_id=question_id, enabled=enabled_status
        )
