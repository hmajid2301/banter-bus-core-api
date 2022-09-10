import pytest
from pytest_mock import MockFixture

from app.player.player_exceptions import PlayerNotHostError
from app.player.player_models import Player
from app.room.room_exceptions import RoomInInvalidState, RoomNotFound
from app.room.room_models import Room, RoomState
from tests.unit.factories import PlayerFactory, RoomFactory
from tests.unit.get_services import get_lobby_service


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_should_kick_player():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_players: list[Player] = PlayerFactory.build_batch(3)
    existing_players[0].player_id = room_host_player_id
    existing_room: Room = RoomFactory.build(
        state=RoomState.CREATED, room_id=room_id, host=room_host_player_id, players=existing_players
    )
    player_to_kick = existing_players[1]

    lobby_service = get_lobby_service(rooms=[existing_room])
    player_kicked = await lobby_service.kick_player(
        player_to_kick_nickname=player_to_kick.nickname,
        player_attempting_kick=room_host_player_id,
        room_id=existing_room.room_id,
    )
    assert player_kicked.nickname == player_to_kick.nickname


@pytest.mark.asyncio
async def test_should_not_kick_player_player_not_host():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    existing_players: list[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    lobby_service = get_lobby_service(rooms=[existing_room], players=existing_players)
    with pytest.raises(PlayerNotHostError):
        await lobby_service.kick_player(
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=existing_players[2].player_id,
            room_id=existing_room.room_id,
        )


@pytest.mark.asyncio
async def test_should_not_kick_player_room_not_found():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    existing_players: list[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    lobby_service = get_lobby_service(rooms=[existing_room], players=existing_players)
    with pytest.raises(RoomNotFound):
        await lobby_service.kick_player(
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=room_host_player_id,
            room_id="BADROOM",
        )


@pytest.mark.asyncio
async def test_should_not_kick_player_invalid_room_state():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED, room_id=room_id, host=room_host_player_id)
    existing_players: list[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    lobby_service = get_lobby_service(rooms=[existing_room], players=existing_players)
    with pytest.raises(RoomInInvalidState):
        await lobby_service.kick_player(
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=room_host_player_id,
            room_id=existing_room.room_id,
        )
