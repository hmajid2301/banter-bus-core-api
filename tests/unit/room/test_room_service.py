import pytest
from pytest_mock import MockFixture

from app.room.room_exceptions import RoomNotFound
from app.room.room_models import Room, RoomState
from tests.unit.factories import RoomFactory
from tests.unit.get_services import get_room_service


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_should_create_room():
    room_service = get_room_service()
    room = await room_service.create()
    assert room.room_id
    assert room.state == RoomState.CREATED


@pytest.mark.asyncio
async def test_should_get_room():
    existing_room: Room = RoomFactory.build()
    room_service = get_room_service(rooms=[existing_room])

    room = await room_service.get(room_id=existing_room.room_id)
    assert room == existing_room


@pytest.mark.asyncio
async def test_should_not_get_room_not_found():
    room_service = get_room_service()
    with pytest.raises(RoomNotFound):
        await room_service.get(room_id="unkown-room-id")
