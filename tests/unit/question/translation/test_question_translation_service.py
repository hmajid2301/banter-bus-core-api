import copy
from typing import List

import pytest
from pytest_mock import MockFixture

from app.question.question_models import Question
from app.question.question_service import QuestionService
from tests.unit.question.fake_question_repository import FakeQuestionRepository
from tests.unit.question.translation.question_translation_service_data import (
    add_question_translation_data,
    add_question_translation_fail_data,
    get_question_translation_data,
    get_question_translation_fail_data,
    remove_question_translation_data,
    remove_question_translation_fail_data,
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
    "game_name, question_id, language_code, content, expected_result",
    add_question_translation_data,
    ids=[
        "add a en quibly round group question",
        "add a ur fibbing_it round group question",
        "add a de drawlosseum round group question",
    ],
)
async def test_add_question_translation(
    game_name: str, question_id: str, language_code: str, content: str, expected_result: dict, questions: List[Question]
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)
    question = await question_service.add_translation(
        game_name=game_name, question_id=question_id, language_code=language_code, content=content
    )
    assert question.dict(by_alias=True, exclude_none=True) == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, language_code, content, expected_exception",
    add_question_translation_fail_data,
    ids=[
        "add a question translation (game not found)",
        "add a question translation (question not found)",
        "add a question translation (language code already exists)",
        "add a question translation (invalid language code)",
    ],
)
async def test_add_question_translation_fail(
    game_name: str, question_id: str, language_code: str, content: str, expected_exception, questions: List[Question]
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(expected_exception):
        await question_service.add_translation(
            game_name=game_name, question_id=question_id, language_code=language_code, content=content
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, language_code, expected_result",
    get_question_translation_data,
    ids=[
        "get a fr quibly round group question",
        "get an en quibly round pair question",
        "get an en fibbing_it round opinion question",
        "get an en fibbing_it round free_form question",
        "get an en fibbing_it round likely question",
        "get an en drawlosseum question",
    ],
)
async def test_get_question_translation(
    game_name: str, question_id: str, language_code: str, expected_result: dict, questions: List[Question]
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)
    question = await question_service.get_translation(
        game_name=game_name, question_id=question_id, language_code=language_code
    )
    assert question.dict(exclude_none=True, by_alias=True) == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, language_code, expected_exception",
    get_question_translation_fail_data,
    ids=[
        "get a question translation (game not found)",
        "get a question translation (question not found)",
        "get a question translation (invalid language code)",
    ],
)
async def test_get_question_translation_fail(
    game_name: str, question_id: str, language_code: str, expected_exception, questions: List[Question]
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(expected_exception):
        await question_service.get_translation(
            game_name=game_name, question_id=question_id, language_code=language_code
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, language_code, expected_result",
    remove_question_translation_data,
    ids=[
        "delete a fr quibly round group question",
        "delete an en quibly round pair question",
        "delete an en fibbing_it round opinion question",
        "delete an en fibbing_it round free_form question",
        "delete an en fibbing_it round likely question",
        "delete an en drawlosseum question",
    ],
)
async def test_remove_question_translation(
    game_name: str, question_id: str, language_code: str, expected_result: dict, questions: List[Question]
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)
    await question_service.remove_translation(game_name=game_name, question_id=question_id, language_code=language_code)

    question = await question_service.get(game_name=game_name, question_id=question_id)
    assert question.dict(by_alias=True, exclude_none=True) == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, question_id, language_code, expected_exception",
    remove_question_translation_fail_data,
    ids=[
        "delete a question translation (game not found)",
        "delete a question translation (question not found)",
        "delete a question translation (invalid language code)",
    ],
)
async def test_remove_question_translation_fail(
    game_name: str, question_id: str, language_code: str, expected_exception, questions: List[Question]
):
    question_repository = FakeQuestionRepository(questions=questions)
    question_service = QuestionService(question_repository=question_repository)

    with pytest.raises(expected_exception):
        await question_service.remove_translation(
            game_name=game_name, question_id=question_id, language_code=language_code
        )
