from typing import List

import pytest
from pytest_mock import MockFixture

from app.game.game_exceptions import GameExists, GameNotFound, InvalidGameFilter
from app.game.game_models import Game
from app.game.game_service import GameService
from tests.unit.factories import GameFactory
from tests.unit.game.fake_game_repository import FakeGameRepository
from tests.unit.game.game_service_data import (
    disable_game_data,
    enable_game_data,
    get_game_name_data,
    update_enable_status_data,
)


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_add_game():
    game_repository = FakeGameRepository(games=[])
    game_service = GameService(game_repository=game_repository)

    game_name = "quibly"
    rules_url = "http://example.com/rules"
    description = "A really fun game"
    display_name = "Quibly"

    game = await game_service.add(
        game_name=game_name, rules_url=rules_url, description=description, display_name=display_name
    )
    expected_game = Game(
        name=game_name, rules_url=rules_url, enabled=True, description=description, display_name=display_name
    )
    assert game == expected_game


@pytest.mark.asyncio
async def test_add_game_that_exists():
    game_name = "quibly"
    rules_url = "http://example.com/rules"
    description = "A really fun game"
    display_name = "Quibly"

    existing_game = Game(
        name=game_name, rules_url=rules_url, enabled=True, description=description, display_name=display_name
    )
    game_repository = FakeGameRepository(games=[existing_game])
    game_service = GameService(game_repository=game_repository)

    with pytest.raises(GameExists):
        await game_service.add(
            game_name=game_name, rules_url=rules_url, description=description, display_name=display_name
        )


@pytest.mark.asyncio
async def test_add_game_game_name_is_unique():
    game_name = "quibly"
    rules_url = "http://example.com/rules"
    description = "A really fun game"
    display_name = "Quibly"

    existing_game = Game(
        name=game_name, rules_url=rules_url, enabled=True, description=description, display_name=display_name
    )
    game_repository = FakeGameRepository(games=[existing_game])
    game_service = GameService(game_repository=game_repository)

    game_name = "quibly2"
    rules_url = "http://example.com/rules"
    description = "A really fun game"
    display_name = "Quibly"

    game = await game_service.add(
        game_name=game_name, rules_url=rules_url, description=description, display_name=display_name
    )
    expected_game = Game(
        name=game_name, rules_url=rules_url, enabled=True, description=description, display_name=display_name
    )
    assert game == expected_game


@pytest.mark.asyncio
async def test_remove_game():
    game_name = "quibly"
    rules_url = "http://example.com/rules"
    description = "A really fun game"
    display_name = "Quibly"

    existing_game = Game(
        name=game_name, rules_url=rules_url, enabled=True, description=description, display_name=display_name
    )
    game_repository = FakeGameRepository(games=[existing_game])
    game_service = GameService(game_repository=game_repository)

    await game_service.remove(game_name=game_name)
    with pytest.raises(GameNotFound):
        await game_repository.get(game_name=game_name)


@pytest.mark.asyncio
async def test_remove_game_does_not_exist():
    game_name = "quibly"
    rules_url = "http://example.com/rules"
    description = "A really fun game"
    display_name = "Quibly"

    existing_game = Game(
        name=game_name, rules_url=rules_url, enabled=True, description=description, display_name=display_name
    )
    game_repository = FakeGameRepository(games=[existing_game])
    game_service = GameService(game_repository=game_repository)

    game_name = "quiblyv2"
    with pytest.raises(GameNotFound):
        await game_service.remove(game_name=game_name)


@pytest.mark.asyncio
async def test_remove_game_no_game_exists():
    game_repository = FakeGameRepository(games=[])
    game_service = GameService(game_repository=game_repository)

    game_name = "quibly"
    with pytest.raises(GameNotFound):
        await game_service.remove(game_name=game_name)


@pytest.mark.asyncio
async def test_get_game():
    game_name = "quibly"
    rules_url = "http://example.com/rules"
    description = "A really fun game"
    display_name = "Quibly"

    existing_game = Game(
        name=game_name, rules_url=rules_url, enabled=True, description=description, display_name=display_name
    )
    game_repository = FakeGameRepository(games=[existing_game])
    game_service = GameService(game_repository=game_repository)

    game = await game_service.get(game_name=game_name)
    assert game == existing_game


@pytest.mark.asyncio
async def test_get_game_does_not_exist():
    game_repository = FakeGameRepository(games=[])
    game_service = GameService(game_repository=game_repository)

    with pytest.raises(GameNotFound):
        await game_service.get(game_name="quibly")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "factory_boy_args, filter, expected_result",
    get_game_name_data,
    ids=[
        "get all games",
        "get all enabled games",
        "get all disabled games (none)",
        "get all disabled games",
        "get all games (mixed enabled state)",
        "get all disabled games (single)",
        "get all enabled games (single)",
    ],
)
async def test_get_game_names(factory_boy_args: dict, filter: str, expected_result: List[str]):
    existing_games = GameFactory.build_batch(**factory_boy_args)
    game_repository = FakeGameRepository(games=existing_games)
    game_service = GameService(game_repository=game_repository)

    games = await game_service.get_game_names(filter=filter)
    assert games == expected_result


@pytest.mark.asyncio
async def test_get_game_names_invalid_filer():
    existing_games = GameFactory.build_batch(3)
    game_repository = FakeGameRepository(games=existing_games)
    game_service = GameService(game_repository=game_repository)

    with pytest.raises(InvalidGameFilter):
        await game_service.get_game_names(filter="invalid")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "factory_boy_args, game_name",
    enable_game_data,
    ids=[
        "enable disabled game (all games disabled)",
        "enable enabled game (all games enabled)",
        "enable disabled game",
        "enable enabled game",
    ],
)
async def test_enable_game(factory_boy_args: dict, game_name: str):
    existing_games = GameFactory.build_batch(**factory_boy_args)
    game_repository = FakeGameRepository(games=existing_games)
    game_service = GameService(game_repository=game_repository)

    game = await game_service.update_enabled_status(game_name=game_name, enabled=True)
    assert game.enabled is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "factory_boy_args, game_name",
    disable_game_data,
    ids=[
        "disable enabled game (all games enabled)",
        "disable enabled game (all games disabled)",
        "disable enabled game",
        "disable disabled game",
    ],
)
async def test_disable_game(factory_boy_args: dict, game_name: str):
    existing_games = GameFactory.build_batch(**factory_boy_args)
    game_repository = FakeGameRepository(games=existing_games)
    game_service = GameService(game_repository=game_repository)

    game = await game_service.update_enabled_status(game_name=game_name, enabled=False)
    assert game.enabled is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "enabled_status",
    update_enable_status_data,
    ids=[
        "enable game",
        "disable game",
    ],
)
async def test_enable_status_game_does_not_exist(enabled_status):
    existing_games = GameFactory.build_batch(3)
    game_repository = FakeGameRepository(games=existing_games)
    game_service = GameService(game_repository=game_repository)

    with pytest.raises(GameNotFound):
        await game_service.update_enabled_status(game_name="quibly_v3", enabled=enabled_status)
