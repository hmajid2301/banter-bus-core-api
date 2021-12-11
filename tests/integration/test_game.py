from typing import List

import pytest
from fastapi import status
from httpx import AsyncClient

from app.game.game_models import Game
from tests.integration.data.game_test_data import (
    add_game_data,
    disabled_game_data,
    enabled_game_data,
    get_game_data,
    get_game_names,
    remove_game_data,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_data, expected_status_code, expected_result",
    add_game_data,
    ids=[
        "Add a new game",
        "Try to add another game, wrong `name` field",
        "Try to add another game, wrong `rules_url` field",
        "Try to add another game, wrong `description` field",
        "Try to add another game, wrong `display_name` field",
        "Try to add a game that already exists",
    ],
)
async def test_add_game(client: AsyncClient, request_data: dict, expected_status_code: int, expected_result: dict):
    response = await client.post("/game", json=request_data)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_201_CREATED:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, expected_status_code",
    remove_game_data,
    ids=[
        "remove an existing game",
        "try to remove a game that does not exist",
    ],
)
async def test_remove_game(client: AsyncClient, game_name: str, expected_status_code: int):
    url = f"/game/{game_name}"
    response = await client.delete(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        game = await Game.find_one(Game.name == game_name)
        assert game is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, expected_status_code, expected_result",
    get_game_data,
    ids=[
        "get a game",
        "get another game",
        "try to get a game that does not exist",
    ],
)
async def test_get_game(client: AsyncClient, game_name: str, expected_status_code: int, expected_result: dict):
    url = f"/game/{game_name}"
    response = await client.get(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filter, expected_status_code, expected_result",
    get_game_names,
    ids=[
        "get all game names",
        "get all game names explicit filter",
        "get all enabled game names",
        "get all disabled game names",
        "get game names invalid filter",
    ],
)
async def test_get_game_names(client: AsyncClient, filter: str, expected_status_code: int, expected_result: List[str]):
    url = f"/game?status={filter}"
    response = await client.get(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, expected_status_code, expected_result",
    enabled_game_data,
    ids=[
        "enable a disabled game",
        "enable an enabled game",
        "try to enable game that does not exist",
    ],
)
async def test_enable_game(client: AsyncClient, game_name: str, expected_status_code: int, expected_result: dict):
    url = f"/game/{game_name}:enable"
    response = await client.put(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "game_name, expected_status_code, expected_result",
    disabled_game_data,
    ids=[
        "disable an enabled game",
        "disable a disabled game",
        "try to disable game that does not exist",
    ],
)
async def test_disable_game(client: AsyncClient, game_name: str, expected_status_code: int, expected_result: dict):
    url = f"/game/{game_name}:disable"
    response = await client.put(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result
