import atexit
import os
import time
from http import HTTPStatus

import pytest
from pactman import Consumer, Like, Provider

from app.clients.management_api.api.games_api import AsyncGamesApi
from app.clients.management_api.exceptions import UnexpectedResponse
from app.room.room_factory import get_game_api


@pytest.fixture(scope="session")
def pact():
    pact = Consumer("core_api").has_pact_with(Provider("management_api"), port=1234, use_mocking_server=True)
    pact.start_mocking()
    time.sleep(0.25)
    yield pact
    atexit.register(pact.stop_mocking)  # type: ignore


@pytest.fixture(scope="session")
def game_api_client() -> AsyncGamesApi:
    os.environ["BANTER_BUS_CORE_API_MANAGEMENT_API_URL"] = "http://localhost"
    os.environ["BANTER_BUS_CORE_API_MANAGEMENT_API_PORT"] = "1234"
    game_api = get_game_api()
    return game_api


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
