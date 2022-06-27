import asyncio
import atexit
import time
from http import HTTPStatus

import pytest
from pactman import Consumer, EachLike, Like, Provider, Term

from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.clients.management_api.exceptions import UnexpectedResponse
from app.core.config import get_settings
from app.game_state.game_state_factory import get_question_api
from app.room.room_factory import get_game_api


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def pact():
    settings = get_settings()
    settings.MANAGEMENT_API_URL = "http://localhost"
    settings.MANAGEMENT_API_PORT = 1234

    pact = Consumer("core_api").has_pact_with(Provider("management_api"), port=1234, use_mocking_server=True)
    pact.start_mocking()
    time.sleep(0.25)
    yield pact
    atexit.register(pact.stop_mocking)


@pytest.fixture(scope="session")
def game_api_client() -> AsyncGamesApi:
    game_api = get_game_api()
    return game_api


@pytest.fixture(scope="session")
def question_api_client() -> AsyncQuestionsApi:
    question_api = get_question_api()
    return question_api


@pytest.mark.asyncio
async def test_enabled_game(pact, game_api_client: AsyncGamesApi):
    expected = {
        "enabled": True,
        "name": "fibbing_it",
        "rules_url": Like("https://gitlab.com/banter-bus/banter-bus-server/-/wikis/docs/rules/fibbing_it"),
        "description": Like(
            "Lie your way through the game, hide the fact you are a spy. Whilst everyone else tried to work it out."
        ),
        "display_name": Like("Fibbing IT!"),
        "minimum_players": Like(4),
        "maximum_players": Like(10),
    }

    pact.given("fibbing_it exists and is enabled").upon_receiving("a request for fibbing_it game info").with_request(
        "GET", "/game/fibbing_it"
    ).will_respond_with(HTTPStatus.OK, body=expected)

    with pact:
        await game_api_client.get_game(game_name="fibbing_it")


@pytest.mark.asyncio
async def test_disabled_game(pact, game_api_client: AsyncGamesApi):
    expected = {
        "enabled": False,
        "name": "quibly",
        "rules_url": Like("https://gitlab.com/banter-bus/banter-bus-server/-/wikis/docs/rules/fibbing_it"),
        "description": Like(
            "Lie your way through the game, hide the fact you are a spy. Whilst everyone else tried to work it out."
        ),
        "display_name": Like("Fibbing IT!"),
        "minimum_players": Like(4),
        "maximum_players": Like(10),
    }

    pact.given("quibly exists and is disabled").upon_receiving("a request for quibly game info").with_request(
        "GET", "/game/quibly"
    ).will_respond_with(HTTPStatus.OK, body=expected)

    with pact:
        await game_api_client.get_game(game_name="quibly")


@pytest.mark.asyncio
async def test_not_found_game(pact, game_api_client: AsyncGamesApi):
    pact.given("quibly2 does not exist").upon_receiving("a request for quibly2 game info").with_request(
        "GET", "/game/quibly2"
    ).will_respond_with(HTTPStatus.NOT_FOUND)

    with pact:
        with pytest.raises(UnexpectedResponse):
            await game_api_client.get_game(game_name="quibly2")


@pytest.mark.asyncio
async def test_get_random_groups(pact, question_api_client: AsyncQuestionsApi):
    expected = {"groups": EachLike("animal_group", minimum=3)}

    pact.given("3 random groups exist for game fibbing_it and round opinion").upon_receiving(
        "a request for getting 3 random groups for game fibbing_it and round opinion"
    ).with_request(
        "GET", "/game/fibbing_it/question/group:random", query={"round": "opinion", "limit": "3"}
    ).will_respond_with(
        HTTPStatus.OK, body=expected
    )

    with pact:
        await question_api_client.get_random_groups(game_name="fibbing_it", round="opinion", limit=3)


@pytest.mark.asyncio
async def test_get_question_from_group(pact, question_api_client: AsyncQuestionsApi):
    expected = EachLike(
        {
            "content": Like("Disagree"),
            "question_id": Like("03a462ba-f483-4726-aeaf-b8b6b03ce3aa"),
            "type": Term("answer|question", "type"),
        },
        minimum=3,
    )

    pact.given("fibbing_it exists and a group called animal_group on round opinion").upon_receiving(
        "a request for getting 3 random questions"
    ).with_request(
        "GET",
        "/game/fibbing_it/question:random",
        query={"round": "opinion", "group_name": "animal_group"},
    ).will_respond_with(
        HTTPStatus.OK, body=expected
    )

    with pact:
        await question_api_client.get_random_questions(
            game_name="fibbing_it", round="opinion", group_name="animal_group"
        )


@pytest.mark.asyncio
async def test_get_question_not_from_group(pact, question_api_client: AsyncQuestionsApi):
    expected = EachLike(
        {
            "content": "to eat ice-cream from the tub",
            "question_id": "d6318b0d-29e1-4f10-b6a7-37a648364ca6",
            "type": "question",
        },
        minimum=3,
    )

    pact.given("fibbing_it exists and a round likely").upon_receiving(
        "a request for getting 3 random questions"
    ).with_request(
        "GET", "/game/fibbing_it/question:random", query={"round": "likely", "limit": "3"}
    ).will_respond_with(
        HTTPStatus.OK, body=expected
    )

    with pact:
        await question_api_client.get_random_questions(game_name="fibbing_it", round="likely", limit=3)
