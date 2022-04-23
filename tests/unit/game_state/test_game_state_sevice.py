from datetime import datetime, timedelta

import pytest
from pytest_httpx import HTTPXMock
from pytest_mock import MockFixture

from app.core.exceptions import GameNotFound
from app.game_state.exceptions import InvalidGameAction
from app.game_state.game_state_models import (
    FibbingActions,
    FibbingItQuestion,
    FibbingItState,
    GameState,
    UpdateQuestionRoundState,
)
from tests.unit.data.data import starting_state
from tests.unit.get_services import get_game_state_service, get_player_service
from tests.unit.mocks import mock_get_questions


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_should_create_new_game(httpx_mock: HTTPXMock):
    game_state_service = get_game_state_service()
    mock_get_questions(httpx_mock)

    room_id = "5b2dd1e9-d8e3-4855-80ef-3bd0acfd481f"
    game_name = "fibbing_it"
    player_service = get_player_service(num=3, room_id=room_id)
    players = await player_service.get_all_in_room(room_id=room_id)

    game_state = await game_state_service.create(room_id=room_id, players=players, game_name=game_name)
    assert game_state.room_id == room_id
    assert isinstance(game_state.state, FibbingItState)
    assert game_state.game_name == game_name

    player_scores = game_state.player_scores
    player_ids = [player.player_id for player in players]
    for player in player_scores:
        assert player.score == 0
        assert player.player_id in player_ids


@pytest.mark.asyncio
async def test_should_not_create_game_not_found():
    room_id = "5b2dd1e9-d8e3-4855-80ef-3bd0acfd481f"
    player_service = get_player_service(num=3, room_id=room_id)
    players = await player_service.get_all_in_room(room_id=room_id)

    game_state_service = get_game_state_service()
    with pytest.raises(GameNotFound):
        await game_state_service.create(room_id=room_id, players=players, game_name="quibly")


@pytest.mark.asyncio
async def test_should_get_first_question_for_fibbing_it(freezer):
    room_id = "5b2dd1e9-d8e3-4855-80ef-3bd0acfd481f"
    game_state = GameState(
        state=starting_state,
        room_id=room_id,
        player_scores=[],
        game_name="fibbing_it",
        next_action=FibbingActions.show_question,
    )

    datetime_ = "2022-04-23T12:34:11Z"
    freezer.move_to(datetime_)
    game_state_service = get_game_state_service(game_states=[game_state])
    question = await game_state_service.get_next_question(game_state=game_state)

    assert isinstance(question.next_question, FibbingItQuestion)
    assert question.next_question.faker_question != question.next_question.question
    assert question.next_question.answers is not None
    assert question.updated_round == UpdateQuestionRoundState(round_changed=False, new_round="opinion")
    assert question.timer_in_seconds == 45

    expected_completed_by_time = datetime.strptime(datetime_, "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=45)
    assert game_state.next_action == FibbingActions.submit_answers
    assert game_state.next_action_completed_by == expected_completed_by_time


@pytest.mark.asyncio
async def test_should_not_get_question_waiting_for_answers():
    room_id = "5b2dd1e9-d8e3-4855-80ef-3bd0acfd481f"
    game_state = GameState(
        state=starting_state,
        room_id=room_id,
        player_scores=[],
        game_name="fibbing_it",
        next_action=FibbingActions.submit_answers,
    )
    game_state_service = get_game_state_service(game_states=[game_state])
    with pytest.raises(InvalidGameAction):
        await game_state_service.get_next_question(game_state=game_state)
