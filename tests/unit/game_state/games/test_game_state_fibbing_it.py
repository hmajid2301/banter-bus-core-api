from typing import List

import pytest
from mergedeep import merge
from pytest_httpx import HTTPXMock
from pytest_mock import MockFixture

from app.game_state.game_state_models import FibbingItQuestion, FibbingItState
from app.player.player_models import Player
from tests.unit.data.data import (
    fibbing_it_get_next_question_data,
    fibbing_it_update_question_data,
    starting_state,
)
from tests.unit.get_services import (
    get_fibbing_it_game,
    get_player_service,
    get_question_api_client,
)
from tests.unit.mocks import mock_get_questions


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_should_get_starting_state(httpx_mock: HTTPXMock):
    fibbing_it = await get_fibbing_it_game()
    mock_get_questions(httpx_mock)
    question_client = get_question_api_client()
    players = await _create_players()
    state = await fibbing_it.get_starting_state(question_client=question_client, players=players)

    assert state.current_round == "opinion"
    player_ids = [player.latest_sid for player in players]
    assert state.current_faker_sid in player_ids

    question_state = state.questions_to_show
    assert question_state.question_nb == -1
    rounds = [question_state.rounds.opinion, question_state.rounds.likely, question_state.rounds.free_form]
    for round_ in rounds:
        assert len(round_) == 3

        for state in round_:
            assert state.faker_question != state.question


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_question_state, expected_state",
    fibbing_it_update_question_data,
    ids=[
        "Update second question opinon round",
        "Update third question opinon round -> likely round",
        "Update first question likely round",
        "Update third question likely round -> free_form round",
        "Don't update third question free_form round",
    ],
)
async def test_should_update_question_state(current_question_state: dict, expected_state: dict):
    fibbing_it = await get_fibbing_it_game()
    new_starting_state = merge(starting_state.dict(), current_question_state)
    fibbing_it_questions = FibbingItState(**new_starting_state)

    updated_state = await fibbing_it.update_question_state(current_state=fibbing_it_questions)
    if not expected_state:
        assert updated_state is None
    else:
        expected_finished_state = merge(starting_state.dict(), expected_state)
        expected_fibbing_it_state = FibbingItState(**expected_finished_state)
        assert updated_state == expected_fibbing_it_state


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_question_state, expected_question",
    fibbing_it_get_next_question_data,
    ids=[
        "Get first question from opinion round",
        "Get second question from likley round",
        "Get third question from free form round",
        "No more questions to show should return None",
    ],
)
async def test_should_get_next_question(current_question_state: dict, expected_question: FibbingItQuestion):
    fibbing_it = await get_fibbing_it_game()
    new_state = merge(starting_state.dict(), current_question_state)
    fibbing_it_questions = FibbingItState(**new_state)

    question = fibbing_it.get_next_question(current_state=fibbing_it_questions)
    assert question == expected_question


async def _create_players() -> List[Player]:
    room_id = "a_random_id"
    player_service = get_player_service(num=3, room_id=room_id)
    players = await player_service.get_all_in_room(room_id=room_id)
    return players
