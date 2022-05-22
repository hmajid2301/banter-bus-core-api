from datetime import datetime, timedelta

import pytest
from pytest_httpx import HTTPXMock
from pytest_mock import MockFixture

from app.core.exceptions import GameNotFound
from app.game_state.game_state_exceptions import (
    GameIsPaused,
    GameStateAlreadyPaused,
    GameStateNotPaused,
    InvalidGameAction,
)
from app.game_state.game_state_models import (
    FibbingActions,
    FibbingItQuestion,
    FibbingItState,
    GamePaused,
    GameState,
    UpdateQuestionRoundState,
)
from tests.unit.factories import GameStateFactory
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
    datetime_ = "2022-04-23T12:34:11Z"
    freezer.move_to(datetime_)

    game_state = GameStateFactory.build(game_name="fibbing_it")
    game_state_service = get_game_state_service(game_states=[game_state])
    question = await game_state_service.get_next_question(game_state=game_state)

    assert isinstance(question.next_question, FibbingItQuestion)
    assert question.next_question.fibber_question != question.next_question.question
    assert question.next_question.answers is not None
    assert question.updated_round == UpdateQuestionRoundState(round_changed=False, new_round="opinion")
    assert question.timer_in_seconds == 45

    expected_completed_by_time = datetime.strptime(datetime_, "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=45)
    assert game_state.action == FibbingActions.submit_answers
    assert game_state.action_completed_by == expected_completed_by_time


@pytest.mark.asyncio
async def test_should_not_get_question_game_is_paused():
    game_state = GameStateFactory.build(paused=GamePaused(is_paused=True, paused_stopped_at=datetime.now()))
    game_state_service = get_game_state_service(game_states=[game_state])

    with pytest.raises(GameIsPaused):
        await game_state_service.get_next_question(game_state=game_state)


@pytest.mark.asyncio
async def test_should_not_get_question_waiting_for_answers():
    game_state = GameStateFactory.build(game_name="fibbing_it", action=FibbingActions.submit_answers)
    game_state_service = get_game_state_service(game_states=[game_state])
    with pytest.raises(InvalidGameAction):
        await game_state_service.get_next_question(game_state=game_state)


@pytest.mark.asyncio
async def test_should_pause_game(freezer):
    datetime_ = "2022-04-23T12:34:11Z"
    freezer.move_to(datetime_)

    game_state: GameState = GameStateFactory.build()
    game_state_service = get_game_state_service(game_states=[game_state])
    await game_state_service.pause_game(room_id=game_state.room_id)

    assert game_state.paused.is_paused is True
    assert str(game_state.paused.paused_stopped_at) == "2022-04-23 12:39:11"


@pytest.mark.asyncio
async def test_should_not_pause_game_already_paused():
    game_state = GameStateFactory.build(paused=GamePaused(is_paused=True))
    game_state_service = get_game_state_service(game_states=[game_state])

    with pytest.raises(GameStateAlreadyPaused):
        await game_state_service.pause_game(room_id=game_state.room_id)


@pytest.mark.asyncio
async def test_should_add_player_to_waiting_for_players_list():
    game_state: GameState = GameStateFactory.build(paused=GamePaused(is_paused=True))
    game_state_service = get_game_state_service(game_states=[game_state])

    await game_state_service.pause_game(room_id=game_state.room_id, player_disconnected="me")
    assert game_state.paused.waiting_for_players == ["me"]


@pytest.mark.asyncio
async def test_should_unpause_game():
    game_state = GameStateFactory.build(paused=GamePaused(is_paused=True))
    game_state_service = get_game_state_service(game_states=[game_state])
    await game_state_service.unpause_game(room_id=game_state.room_id)

    assert game_state.paused.is_paused is False


@pytest.mark.asyncio
async def test_should_not_unpause_game_already_unpaused():
    game_state: GameState = GameStateFactory.build()
    game_state_service = get_game_state_service(game_states=[game_state])

    with pytest.raises(GameStateNotPaused):
        await game_state_service.unpause_game(room_id=game_state.room_id)


@pytest.mark.asyncio
async def test_should_remove_player_from_waiting_for_players_list():
    game_state: GameState = GameStateFactory.build(paused=GamePaused(is_paused=True, waiting_for_players=["me"]))
    game_state_service = get_game_state_service(game_states=[game_state])

    await game_state_service.unpause_game(room_id=game_state.room_id, player_reconnected="me")
    assert game_state.paused.waiting_for_players == []
