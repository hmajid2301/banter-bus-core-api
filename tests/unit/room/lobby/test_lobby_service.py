from typing import List

import pytest
from pytest_mock import MockFixture

from app.player.player_exceptions import PlayerNotFound
from app.player.player_models import NewPlayer, Player
from app.room.room_exceptions import (
    NicknameExistsException,
    RoomHasNoHostError,
    RoomNotFound,
    RoomNotJoinableError,
)
from app.room.room_models import Room, RoomState
from tests.unit.common import get_lobby_service, get_player_service, get_room_service
from tests.unit.factories import PlayerFactory, RoomFactory, get_new_player


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_should_join_empty_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    new_player = get_new_player()
    player_service = get_player_service()
    room_players = await lobby_service.join(
        player_service=player_service, room_id=existing_room.room_id, new_player=new_player
    )

    expected_player = Player(**new_player.dict(), room_id=existing_room.room_id, player_id=room_players.player_id)
    assert room_players.players == [expected_player]
    assert room_players.host_player_nickname == expected_player.nickname


@pytest.mark.asyncio
async def test_should_not_join_finished_room():
    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    new_player = get_new_player()
    player_service = get_player_service()

    with pytest.raises(RoomNotJoinableError):
        await lobby_service.join(player_service=player_service, room_id=existing_room.room_id, new_player=new_player)


@pytest.mark.asyncio
async def test_should_join_non_empty_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players, nickname="majiy")
    existing_room.host = existing_players[0].player_id

    new_player = get_new_player()
    room_players = await lobby_service.join(
        player_service=player_service, room_id=existing_room.room_id, new_player=new_player
    )

    expected_player = Player(**new_player.dict(), room_id=existing_room.room_id, player_id=room_players.player_id)
    expected_players = [expected_player, *existing_players]
    assert _sort_list_by_player_id(room_players.players) == _sort_list_by_player_id(expected_players)
    assert room_players.host_player_nickname != expected_player.nickname


@pytest.mark.asyncio
async def test_should_not_join_room_nickname_exists():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    existing_room.host = existing_players[0].player_id

    player: Player = PlayerFactory.build(nickname=existing_players[0].nickname)
    new_player = NewPlayer(**player.dict())

    with pytest.raises(NicknameExistsException):
        await lobby_service.join(player_service=player_service, room_id=existing_room.room_id, new_player=new_player)


@pytest.mark.asyncio
async def test_should_rejoin_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = first_player_id

    room_players = await lobby_service.rejoin(
        player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid
    )
    assert room_players.host_player_nickname == existing_players[0].nickname
    assert _sort_list_by_player_id(room_players.players) == _sort_list_by_player_id(existing_players)


@pytest.mark.asyncio
async def test_should_not_rejoin_in_finished_room():
    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = first_player_id

    with pytest.raises(RoomNotJoinableError):
        await lobby_service.rejoin(
            player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid
        )


@pytest.mark.asyncio
async def test_should_not_rejoin_room_player_not_found():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = existing_players[0].player_id

    with pytest.raises(PlayerNotFound):
        await lobby_service.rejoin(
            player_service=player_service, player_id="player-id-unknown", latest_sid=first_player_sid
        )


@pytest.mark.asyncio
async def test_should_not_rejoin_room_has_no_host():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid

    with pytest.raises(RoomHasNoHostError):
        await lobby_service.rejoin(
            player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid
        )


@pytest.mark.asyncio
async def test_should_not_rejoin_room_not_found():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    lobby_service = get_lobby_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id="unknown-room-id")
    player_service = get_player_service(players=existing_players)
    existing_room.host = existing_players[0].player_id

    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid

    with pytest.raises(RoomNotFound):
        await lobby_service.rejoin(
            player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid
        )


@pytest.mark.asyncio
async def test_should_update_room_host():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_disconnected = existing_players[1]

    player_service = get_player_service(existing_players)
    lobby_service = get_lobby_service(rooms=[existing_room])

    await lobby_service.update_host(
        player_service=player_service, room=existing_room, old_host_id=player_disconnected.player_id
    )

    room_service = get_room_service(rooms=[existing_room])
    room = await room_service.get(room_id=existing_room.room_id)
    assert not room.host == player_disconnected.player_id


def _sort_list_by_player_id(players: List[Player]):
    players.sort(key=lambda p: p.player_id, reverse=True)
