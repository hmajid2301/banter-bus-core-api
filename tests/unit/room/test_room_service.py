import pytest
from pytest_mock import MockFixture

from app.player.player_exceptions import PlayerNotHostError
from app.room.room_exceptions import RoomInInvalidState, RoomNotFound
from app.room.room_models import Room, RoomState
from tests.unit.factories import GameStateFactory, RoomFactory
from tests.unit.get_services import get_game_state_service, get_room_service


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


@pytest.mark.asyncio
async def test_should_pause_room():
    existing_room: Room = RoomFactory.build(state=RoomState.PLAYING, host="me")
    room_service = get_room_service(rooms=[existing_room])
    game_state = GameStateFactory.build(room_id=existing_room.room_id)
    game_state_service = get_game_state_service(game_states=[game_state])

    paused_for_seconds = await room_service.pause_game(
        room_id=existing_room.room_id, player_id=existing_room.host or "", game_state_service=game_state_service
    )
    assert paused_for_seconds == 300


@pytest.mark.asyncio
async def test_should_not_pause_room_player_not_host():
    existing_room: Room = RoomFactory.build(state=RoomState.PLAYING, host="me")
    room_service = get_room_service(rooms=[existing_room])
    game_state = GameStateFactory.build(room_id=existing_room.room_id)
    game_state_service = get_game_state_service(game_states=[game_state])

    with pytest.raises(PlayerNotHostError):
        await room_service.pause_game(
            room_id=existing_room.room_id, player_id="host-abc", game_state_service=game_state_service
        )


@pytest.mark.asyncio
async def test_should_not_pause_room_invalid_state():
    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED, host="me")
    room_service = get_room_service(rooms=[existing_room])
    game_state = GameStateFactory.build(room_id=existing_room.room_id)
    game_state_service = get_game_state_service(game_states=[game_state])

    with pytest.raises(RoomInInvalidState):
        await room_service.pause_game(
            room_id=existing_room.room_id, player_id=existing_room.host or "", game_state_service=game_state_service
        )
