import pytest
from pytest_httpx import HTTPXMock
from pytest_mock import MockFixture

from app.player.player_exceptions import PlayerNotHostError
from app.player.player_models import Player
from app.room.room_exceptions import (
    GameNotEnabled,
    RoomInInvalidState,
    RoomNotFound,
    TooFewPlayersInRoomError,
    TooManyPlayersInRoomError,
)
from app.room.room_models import Room, RoomState
from tests.unit.factories import PlayerFactory, RoomFactory
from tests.unit.get_services import get_game_api_client, get_lobby_service
from tests.unit.mocks import mock_get_game, mock_get_questions


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_should_start_game(httpx_mock: HTTPXMock):
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(
        state=RoomState.CREATED, room_id=room_id, host=room_host_player_id, player_count=2
    )
    existing_players: list[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    lobby_service = get_lobby_service(rooms=[existing_room], players=existing_players)
    game_api = get_game_api_client()

    mock_get_game(httpx_mock)
    mock_get_questions(httpx_mock)
    room = await lobby_service.start_game(
        game_api=game_api, game_name="fibbing_it", room_id=existing_room.room_id, player_id=room_host_player_id
    )
    assert room.state == RoomState.PLAYING


@pytest.mark.asyncio
async def test_should_not_start_game_room_playing_game():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.PLAYING, room_id=room_id, host=room_host_player_id)
    lobby_service = get_lobby_service(rooms=[existing_room])
    game_api = get_game_api_client()

    with pytest.raises(RoomInInvalidState):
        await lobby_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id=existing_room.room_id, player_id=room_host_player_id
        )


@pytest.mark.asyncio
async def test_should_start_game_game_disabled(httpx_mock: HTTPXMock):
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    lobby_service = get_lobby_service(rooms=[existing_room])
    game_api = get_game_api_client()

    mock_get_game(httpx_mock, enabled=False)
    with pytest.raises(GameNotEnabled):
        await lobby_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id=existing_room.room_id, player_id=room_host_player_id
        )


@pytest.mark.asyncio
async def test_should_not_start_game_room_not_found():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    lobby_service = get_lobby_service(rooms=[existing_room])
    game_api = get_game_api_client()

    with pytest.raises(RoomNotFound):
        await lobby_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id="random-room-id", player_id=room_host_player_id
        )


@pytest.mark.asyncio
async def test_should_not_start_game_player_not_host():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    lobby_service = get_lobby_service(rooms=[existing_room])
    game_api = get_game_api_client()

    with pytest.raises(PlayerNotHostError):
        await lobby_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id=room_id, player_id="another_player_id"
        )


@pytest.mark.asyncio
async def test_should_not_start_game_too_many_players(httpx_mock: HTTPXMock):
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(
        state=RoomState.CREATED, room_id=room_id, host=room_host_player_id, players=PlayerFactory.build_batch(11)
    )
    lobby_service = get_lobby_service(rooms=[existing_room])
    game_api = get_game_api_client()

    mock_get_game(httpx_mock)
    with pytest.raises(TooManyPlayersInRoomError):
        await lobby_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id=room_id, player_id=room_host_player_id
        )


@pytest.mark.asyncio
async def test_should_not_start_game_too_few_players(httpx_mock: HTTPXMock):
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(
        state=RoomState.CREATED, room_id=room_id, host=room_host_player_id, players=PlayerFactory.build_batch(0)
    )
    lobby_service = get_lobby_service(rooms=[existing_room])
    game_api = get_game_api_client()

    mock_get_game(httpx_mock)
    with pytest.raises(TooFewPlayersInRoomError):
        await lobby_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id=room_id, player_id=room_host_player_id
        )
