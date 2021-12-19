import pytest
from pytest_mock import MockFixture

from app.room.room_exceptions import GameNotEnabled, GameNotFound
from app.room.room_models import GameState
from app.room.room_service import RoomService
from tests.data.management_api_game import games
from tests.unit.room.fake_game_api import FakeGameAPI
from tests.unit.room.fake_room_repository import FakeRoomRepository


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_create_room():
    room_repository = FakeRoomRepository(rooms=[])
    management_client = FakeGameAPI(games=games)
    room_service = RoomService(room_repository=room_repository)

    game_name = "quibly"

    room = await room_service.create(game_name=game_name, management_client=management_client)
    assert room.room_id
    assert room.game_name == game_name
    assert room.room_code
    assert room.state == GameState.CREATED
    assert room.players == []


@pytest.mark.asyncio
async def test_create_room_disabled_game():
    room_repository = FakeRoomRepository(rooms=[])
    management_client = FakeGameAPI(games=games)
    room_service = RoomService(room_repository=room_repository)

    game_name = "drawlosseum"

    with pytest.raises(GameNotEnabled):
        await room_service.create(game_name=game_name, management_client=management_client)


@pytest.mark.asyncio
async def test_create_room_game_not_found():
    room_repository = FakeRoomRepository(rooms=[])
    management_client = FakeGameAPI(games=games)
    room_service = RoomService(room_repository=room_repository)

    game_name = "quibly_v2"

    with pytest.raises(GameNotFound):
        await room_service.create(game_name=game_name, management_client=management_client)
