from typing import List

import pytest
from pytest_mock import MockFixture

from app.player.player_exceptions import PlayerNotFound, PlayerNotHostError
from app.player.player_models import NewPlayer, Player
from app.player.player_service import PlayerService
from app.room.room_exceptions import (
    NicknameExistsException,
    RoomHasNoHostError,
    RoomInInvalidState,
    RoomNotFound,
    RoomNotJoinableError,
)
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
    assert room.state == RoomState.CREATED


@pytest.mark.asyncio
async def test_get_room():
    existing_room: Room = RoomFactory.build()
    room_service = _get_room_service(rooms=[existing_room])

    room = await room_service.get(room_id=existing_room.room_id)
    assert room == existing_room


@pytest.mark.asyncio
async def test_get_room_not_found():
    room_service = _get_room_service()
    with pytest.raises(RoomNotFound):
        await room_service.get(room_id="unkown-room-id")


@pytest.mark.asyncio
async def test_join_empty_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = _get_room_service(rooms=[existing_room])

    new_player = get_new_player()
    player_service = _get_player_service()
    room_players = await room_service.join(
        player_service=player_service, room_id=existing_room.room_id, new_player=new_player
    )

    expected_player = Player(**new_player.dict(), room_id=existing_room.room_id, player_id=room_players.player_id)
    assert room_players.players == [expected_player]
    assert room_players.host_player_nickname == expected_player.nickname


@pytest.mark.asyncio
async def test_join_finished_room():
    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED)
    room_service = _get_room_service(rooms=[existing_room])

    new_player = get_new_player()
    player_service = _get_player_service()

    with pytest.raises(RoomNotJoinableError):
        await room_service.join(player_service=player_service, room_id=existing_room.room_id, new_player=new_player)


@pytest.mark.asyncio
async def test_join_non_empty_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = _get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = _get_player_service(players=existing_players, nickname="majiy")
    existing_room.host = existing_players[0].player_id

    new_player = get_new_player()
    room_players = await room_service.join(
        player_service=player_service, room_id=existing_room.room_id, new_player=new_player
    )

    expected_player = Player(**new_player.dict(), room_id=existing_room.room_id, player_id=room_players.player_id)
    expected_players = [expected_player, *existing_players]
    assert _sort_list_by_player_id(room_players.players) == _sort_list_by_player_id(expected_players)
    assert room_players.host_player_nickname != expected_player.nickname


@pytest.mark.asyncio
async def test_join_nickname_exists():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = _get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = _get_player_service(players=existing_players)
    existing_room.host = existing_players[0].player_id

    player: Player = PlayerFactory.build(nickname=existing_players[0].nickname)
    new_player = NewPlayer(**player.dict())

    with pytest.raises(NicknameExistsException):
        await room_service.join(player_service=player_service, room_id=existing_room.room_id, new_player=new_player)


@pytest.mark.asyncio
async def test_rejoin_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = _get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = _get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = first_player_id

    room_players = await room_service.rejoin(
        player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid
    )
    assert room_players.host_player_nickname == existing_players[0].nickname
    assert _sort_list_by_player_id(room_players.players) == _sort_list_by_player_id(existing_players)


@pytest.mark.asyncio
async def test_rejoin_finished_room():
    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED)
    room_service = _get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = _get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = first_player_id

    with pytest.raises(RoomNotJoinableError):
        await room_service.rejoin(player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid)


@pytest.mark.asyncio
async def test_rejoin_room_player_not_found():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = _get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = _get_player_service(players=existing_players)
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = existing_players[0].player_id

    with pytest.raises(PlayerNotFound):
        await room_service.rejoin(
            player_service=player_service, player_id="player-id-unknown", latest_sid=first_player_sid
        )


@pytest.mark.asyncio
async def test_rejoin_room_no_host():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = _get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = _get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid

    with pytest.raises(RoomHasNoHostError):
        await room_service.rejoin(player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid)


@pytest.mark.asyncio
async def test_rejoin_room_not_found():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = _get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id="unknown-room-id")
    player_service = _get_player_service(players=existing_players)
    existing_room.host = existing_players[0].player_id

    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid

    with pytest.raises(RoomNotFound):
        await room_service.rejoin(player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid)


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


@pytest.mark.asyncio
async def test_kick_player():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    player_service = _get_player_service(existing_players)
    room_service = _get_room_service(rooms=[existing_room])

    player_kicked_nickname = await room_service.kick_player(
        player_service=player_service,
        player_to_kick_nickname=player_to_kick.nickname,
        player_attempting_kick=room_host_player_id,
        room_id=existing_room.room_id,
    )
    assert player_kicked_nickname == player_to_kick.nickname


@pytest.mark.asyncio
async def test_kick_player_player_not_host():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    player_service = _get_player_service(existing_players)
    room_service = _get_room_service(rooms=[existing_room])

    with pytest.raises(PlayerNotHostError):
        await room_service.kick_player(
            player_service=player_service,
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=existing_players[2].player_id,
            room_id=existing_room.room_id,
        )


@pytest.mark.asyncio
async def test_kick_player_room_not_found():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    player_service = _get_player_service(existing_players)
    room_service = _get_room_service(rooms=[existing_room])

    with pytest.raises(RoomNotFound):
        await room_service.kick_player(
            player_service=player_service,
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=room_host_player_id,
            room_id="BADROOM",
        )


@pytest.mark.asyncio
async def test_kick_player_invalid_room_state():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED, room_id=room_id, host=room_host_player_id)
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    player_service = _get_player_service(existing_players)
    room_service = _get_room_service(rooms=[existing_room])

    with pytest.raises(RoomInInvalidState):
        await room_service.kick_player(
            player_service=player_service,
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=room_host_player_id,
            room_id=existing_room.room_id,
        )


def _sort_list_by_player_id(players: List[Player]):
    players.sort(key=lambda p: p.player_id, reverse=True)


def _get_room_service(rooms: List[Room] = [], num: int = 1, **kwargs) -> RoomService:
    if rooms:
        existing_room = rooms
    elif num:
        existing_room = RoomFactory.build_batch(num, **kwargs)
    else:
        existing_room = []

    room_repository = FakeRoomRepository(rooms=existing_room)
    room_service = RoomService(room_repository=room_repository)
    return room_service


def _get_player_service(players: List[Player] = [], num: int = 1, **kwargs) -> PlayerService:
    if players:
        existing_players = players
    elif num:
        existing_players = PlayerFactory.build_batch(num, **kwargs)
    else:
        existing_players = []

    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)
    return player_service
