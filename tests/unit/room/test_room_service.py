from typing import List

import pytest
from pytest_mock import MockFixture

from app.player.player_exceptions import PlayerNotFound
from app.player.player_models import NewPlayer, Player
from app.player.player_service import PlayerService
from app.room.room_exceptions import NicknameExistsException, RoomNotFound
from app.room.room_models import Room, RoomState
from app.room.room_service import RoomService
from tests.unit.factories import PlayerFactory, RoomFactory, get_new_player
from tests.unit.player.fake_player_repository import FakePlayerRepository
from tests.unit.room.fake_room_repository import FakeRoomRepository


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_create_room():
    room_repository = FakeRoomRepository(rooms=[])
    room_service = RoomService(room_repository=room_repository)

    room = await room_service.create()
    assert room.room_id
    assert room.room_code
    assert room.state == RoomState.CREATED


@pytest.mark.asyncio
async def test_get_open_room():
    room_code = "ABCDEabcde12"
    existing_room = RoomFactory.build(room_code=room_code, state=RoomState.CREATED)
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    existing_room = await room_service._get_by_room_code(room_code=room_code)
    assert existing_room.room_code == room_code


@pytest.mark.asyncio
async def test_get_room():
    existing_room: Room = RoomFactory.build()
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    room = await room_service.get(room_id=existing_room.room_id)
    assert room == existing_room


@pytest.mark.asyncio
async def test_get_room_not_found():
    existing_room: Room = RoomFactory.build()
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    with pytest.raises(RoomNotFound):
        await room_service.get(room_id="unkown-room-id")


@pytest.mark.asyncio
async def test_join_empty_room():
    player_repository = FakePlayerRepository(players=[])
    player_service = PlayerService(player_repository=player_repository)

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    new_player = get_new_player()
    room_players = await room_service.join(
        player_service=player_service, room_code=existing_room.room_code, new_player=new_player
    )

    expected_player = Player(**new_player.dict(), room_id=existing_room.room_id, player_id=room_players.player_id)
    assert room_players.players == [expected_player]
    assert room_players.host_player_nickname == expected_player.nickname


@pytest.mark.asyncio
async def test_join_non_empty_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_repository = FakePlayerRepository(players=[*existing_players])
    player_service = PlayerService(player_repository=player_repository)
    existing_room.host = existing_players[0].player_id

    new_player = get_new_player()
    room_players = await room_service.join(
        player_service=player_service, room_code=existing_room.room_code, new_player=new_player
    )

    expected_player = Player(**new_player.dict(), room_id=existing_room.room_id, player_id=room_players.player_id)
    expected_players = [expected_player, *existing_players]
    assert _sort_list_by_player_id(room_players.players) == _sort_list_by_player_id(expected_players)
    assert room_players.host_player_nickname != expected_player.nickname


@pytest.mark.asyncio
async def test_join_nickname_exists():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)
    existing_room.host = existing_players[0].player_id

    player: Player = PlayerFactory.build(nickname=existing_players[0].nickname)
    new_player = NewPlayer(**player.dict())

    with pytest.raises(NicknameExistsException):
        await room_service.join(player_service=player_service, room_code=existing_room.room_code, new_player=new_player)


@pytest.mark.asyncio
async def test_rejoin_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)
    first_player_id = existing_players[0].player_id
    existing_room.host = first_player_id

    room_players = await room_service.rejoin(player_service=player_service, player_id=first_player_id)
    assert room_players.host_player_nickname == existing_players[0].nickname
    assert _sort_list_by_player_id(room_players.players) == _sort_list_by_player_id(existing_players)


@pytest.mark.asyncio
async def test_rejoin_room_player_not_found():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_repository = FakePlayerRepository(players=[*existing_players])
    player_service = PlayerService(player_repository=player_repository)
    existing_room.host = existing_players[0].player_id

    with pytest.raises(PlayerNotFound):
        await room_service.rejoin(player_service=player_service, player_id="player-id-unknown")


@pytest.mark.asyncio
async def test_rejoin_room_not_found():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_repository = FakeRoomRepository(rooms=[existing_room])
    room_service = RoomService(room_repository=room_repository)

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id="unknown-room-id")
    player_repository = FakePlayerRepository(players=[*existing_players])
    player_service = PlayerService(player_repository=player_repository)
    existing_room.host = existing_players[0].player_id

    first_player_id = existing_players[0].player_id
    with pytest.raises(RoomNotFound):
        await room_service.rejoin(player_service=player_service, player_id=first_player_id)


@pytest.mark.asyncio
async def test_get_room_players():
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    room_players = RoomService._get_room_players(
        room_host_player_id=room_host_player_id,
        players=existing_players,
        player_id=room_host_player_id,
        room_code="ANCDEFH",
    )
    assert room_players.host_player_nickname == existing_players[0].nickname
    assert _sort_list_by_player_id(room_players.players) == _sort_list_by_player_id(existing_players)


def _sort_list_by_player_id(players: List[Player]):
    players.sort(key=lambda p: p.player_id, reverse=True)
