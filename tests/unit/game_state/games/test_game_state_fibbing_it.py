from datetime import datetime, timedelta
from typing import Any

import pytest
from mergedeep import merge
from pytest_httpx import HTTPXMock
from pytest_mock import MockFixture

from app.game_state.game_state_exceptions import ActionTimedOut
from app.game_state.game_state_models import (
    FibbingActions,
    FibbingItQuestion,
    FibbingItQuestionsState,
    FibbingItRounds,
    FibbingItState,
    GamePaused,
    GameState,
    PlayerScore,
)
from app.game_state.games.exceptions import InvalidAnswer
from app.player.player_models import Player
from tests.unit.data.data import (
    fibbing_it_get_next_question_data,
    fibbing_it_update_question_data,
    starting_state,
)
from tests.unit.factories import GameStateFactory
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
    fibbing_it = get_fibbing_it_game()
    mock_get_questions(httpx_mock)
    question_client = get_question_api_client()
    players = await _create_players()
    state = await fibbing_it.get_starting_state(question_client=question_client, players=players)

    assert state.current_round == "opinion"
    player_ids = [player.player_id for player in players]
    assert state.current_fibber_id in player_ids

    question_state = state.questions
    assert question_state.question_nb == -1
    rounds = [question_state.rounds.opinion, question_state.rounds.likely, question_state.rounds.free_form]
    for round_ in rounds:
        assert len(round_) == 3

        for state_ in round_:
            assert state_.fibber_question != state_.question


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
async def test_should_update_question_state(current_question_state: dict[Any, Any], expected_state: dict[Any, Any]):
    fibbing_it = get_fibbing_it_game()
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
async def test_should_get_next_question(current_question_state: dict[Any, Any], expected_question: FibbingItQuestion):
    fibbing_it = get_fibbing_it_game()
    new_state = merge(starting_state.dict(), current_question_state)
    fibbing_it_questions = FibbingItState(**new_state)

    question = fibbing_it.get_next_question(current_state=fibbing_it_questions)
    assert question == expected_question


async def _create_players() -> list[Player]:
    room_id = "a_random_id"
    player_service = get_player_service(num=3, room_id=room_id)
    players = await player_service.get_all_in_room(room_id=room_id)
    return players


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "round_, answer",
    [
        ("opinion", "lame"),
        ("likely", "9d2dd1e9-d8e3-4855-80ef-3bd0acfd48dd"),
    ],
    ids=[
        "Submit answer to round opinion with answer lame",
        "Submit answer to round likely with answer correct player id",
    ],
)
async def test_should_submit_answers(round_: str, answer: str):
    room_id = "5b2dd1e9-d8e3-4855-80ef-3bd0acfd481f"

    state = _get_game_state(round_=round_)
    game_state: GameState = GameStateFactory.build(
        room_id=room_id,
        action=FibbingActions.submit_answers,
        state=state.state,
        action_completed_by=datetime.now() + timedelta(minutes=5),
    )
    player_service = get_player_service(num=3, room_id=room_id)
    players = await player_service.get_all_in_room(room_id=room_id)

    fibbing_it = get_fibbing_it_game()
    player_id = players[0].player_id
    players[1].player_id = "9d2dd1e9-d8e3-4855-80ef-3bd0acfd48dd"

    player_ids = [player.player_id for player in players]
    new_state = fibbing_it.submit_answers(
        game_state=game_state,
        player_id=player_id,
        player_ids=player_ids,
        answer=answer,
    )
    assert new_state.questions.current_answers[player_id] == answer


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "round_, answer",
    [
        ("opinion", "not lame"),
        ("likely", "dd2dd1e9-d8e3-4855-80ef-3bd0acfd48dd"),
    ],
    ids=[
        "Submit answer to round opinion with answer not lame",
        "Submit answer to round likely with answer incorrect player id",
    ],
)
async def test_should_not_submit_answers_invalid_answer(round_: str, answer: str):
    room_id = "5b2dd1e9-d8e3-4855-80ef-3bd0acfd481f"

    state = _get_game_state(round_=round_)
    game_state: GameState = GameStateFactory.build(
        room_id=room_id,
        action=FibbingActions.submit_answers,
        state=state.state,
        action_completed_by=datetime.now() + timedelta(minutes=5),
    )
    player_service = get_player_service(num=3, room_id=room_id)
    players = await player_service.get_all_in_room(room_id=room_id)

    fibbing_it = get_fibbing_it_game()
    player_id = players[0].player_id

    player_ids = [player.player_id for player in players]
    with pytest.raises(InvalidAnswer):
        fibbing_it.submit_answers(
            game_state=game_state,
            player_id=player_id,
            player_ids=player_ids,
            answer=answer,
        )


@pytest.mark.asyncio
async def test_should_not_submit_answers_timed_out():
    room_id = "5b2dd1e9-d8e3-4855-80ef-3bd0acfd481f"

    state = _get_game_state(round_="opinion")
    game_state: GameState = GameStateFactory.build(
        room_id=room_id,
        action=FibbingActions.submit_answers,
        state=state.state,
        action_completed_by=datetime.now() - timedelta(minutes=5),
    )
    player_service = get_player_service(num=3, room_id=room_id)
    players = await player_service.get_all_in_room(room_id=room_id)

    fibbing_it = get_fibbing_it_game()
    player_id = players[0].player_id

    player_ids = [player.player_id for player in players]
    with pytest.raises(ActionTimedOut):
        fibbing_it.submit_answers(
            game_state=game_state,
            player_id=player_id,
            player_ids=player_ids,
            answer="lame",
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "round_",
    ["opinion", "likely", "free_form"],
    ids=[
        "Select random answer for round opinion",
        "Select random answer for round likely",
        "Select empty answer for round free_form",
    ],
)
async def test_should_select_random_answers(round_: str):
    room_id = "5b2dd1e9-d8e3-4855-80ef-3bd0acfd481f"

    state = _get_game_state(round_=round_)
    player_service = get_player_service(num=3, room_id=room_id)
    players = await player_service.get_all_in_room(room_id=room_id)

    fibbing_it = get_fibbing_it_game()
    player_ids = [player.player_id for player in players]
    fibbing_it_state = FibbingItState(**state.state.dict())
    new_state = fibbing_it.select_random_answer(state=fibbing_it_state, player_ids=player_ids)

    answers = new_state.questions.current_answers
    for player_id in player_ids:
        assert answers[player_id] is not None


def _get_game_state(round_="opinion"):
    return GameState(
        paused=GamePaused(),
        room_id="2257856e-bf37-4cc4-8551-0b1ccdc38c60",
        game_name="fibbing_it",
        player_scores=[
            PlayerScore(player_id="5fcfe479-1984-471d-bd23-136e85696da4", score=0),
            PlayerScore(player_id="f921d6cf-b59f-4a3c-9e58-f0273121cc1a", score=0),
            PlayerScore(player_id="285243e1-0656-44cc-9549-fea3a17e2540", score=0),
        ],
        action=FibbingActions.show_question,
        state=FibbingItState(
            current_fibber_id="8cdc1984-e832-48c7-9d89-1d724665bef1",
            questions=FibbingItQuestionsState(
                rounds=FibbingItRounds(
                    opinion=[
                        FibbingItQuestion(
                            fibber_question="What do you think about horses?",
                            question="What do you think about camels?",
                            answers=["lame", "tasty", "cool"],
                        ),
                        FibbingItQuestion(
                            fibber_question="Dogs are cute?",
                            question="Cats are cuter than dogs?",
                            answers=["Agree", "Strongly Agree", "Disagree"],
                        ),
                        FibbingItQuestion(
                            fibber_question="What is your least favourite colour?",
                            question="What is your favourite colour?",
                            answers=["red", "blue"],
                        ),
                    ],
                    likely=[
                        FibbingItQuestion(
                            fibber_question="Least likely to get arrested",
                            question="Most likely to get arrested",
                            answers=["Richard", "Michael", "Brandon"],
                        ),
                        FibbingItQuestion(
                            fibber_question="Most likely to fight a horse and lose",
                            question="Most likely to eat a tub of ice-cream",
                            answers=["Richard", "Michael", "Brandon"],
                        ),
                        FibbingItQuestion(
                            fibber_question="Most likely to eat a tub of ice-cream",
                            question="Most likely to fight a horse and lose",
                            answers=["Richard", "Michael", "Brandon"],
                        ),
                    ],
                    free_form=[
                        FibbingItQuestion(
                            fibber_question="A funny question?", question="Favourite bike colour?", answers=None
                        ),
                        FibbingItQuestion(
                            fibber_question="what do you like about cats?",
                            question="what don't you like about cats?",
                            answers=None,
                        ),
                        FibbingItQuestion(
                            fibber_question="Favourite fruit", question="Least favourite fruit", answers=None
                        ),
                    ],
                ),
                question_nb=0,
                current_answers={},
            ),
            current_round=round_,
        ),
    )
