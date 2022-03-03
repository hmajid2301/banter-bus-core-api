from typing import List

import pytest
from pytest_httpx import HTTPXMock
from pytest_mock import MockFixture

from app.clients.management_api.models import GameOut
from app.player.player_exceptions import PlayerNotFound, PlayerNotHostError
from app.player.player_models import NewPlayer, Player
from app.room.room_exceptions import (
    GameNotEnabled,
    NicknameExistsException,
    RoomHasNoHostError,
    RoomInInvalidState,
    RoomNotFound,
    RoomNotJoinableError,
)
from app.room.room_models import Room, RoomState
from app.room.room_service import RoomService
from tests.unit.common import get_game_api_client, get_player_service, get_room_service
from tests.unit.factories import PlayerFactory, RoomFactory, get_new_player
from tests.unit.room.fake_room_repository import FakeRoomRepository


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_should_create_room():
    room_repository = FakeRoomRepository(rooms=[])
    room_service = RoomService(room_repository=room_repository)

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
async def test_should_join_empty_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = get_room_service(rooms=[existing_room])

    new_player = get_new_player()
    player_service = get_player_service()
    room_players = await room_service.join(
        player_service=player_service, room_id=existing_room.room_id, new_player=new_player
    )

    expected_player = Player(**new_player.dict(), room_id=existing_room.room_id, player_id=room_players.player_id)
    assert room_players.players == [expected_player]
    assert room_players.host_player_nickname == expected_player.nickname


@pytest.mark.asyncio
async def test_should_not_join_finished_room():
    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED)
    room_service = get_room_service(rooms=[existing_room])

    new_player = get_new_player()
    player_service = get_player_service()

    with pytest.raises(RoomNotJoinableError):
        await room_service.join(player_service=player_service, room_id=existing_room.room_id, new_player=new_player)


@pytest.mark.asyncio
async def test_should_join_non_empty_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players, nickname="majiy")
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
async def test_should_not_join_room_nickname_exists():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    existing_room.host = existing_players[0].player_id

    player: Player = PlayerFactory.build(nickname=existing_players[0].nickname)
    new_player = NewPlayer(**player.dict())

    with pytest.raises(NicknameExistsException):
        await room_service.join(player_service=player_service, room_id=existing_room.room_id, new_player=new_player)


@pytest.mark.asyncio
async def test_should_rejoin_room():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = first_player_id

    room_players = await room_service.rejoin(
        player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid
    )
    assert room_players.host_player_nickname == existing_players[0].nickname
    assert _sort_list_by_player_id(room_players.players) == _sort_list_by_player_id(existing_players)


@pytest.mark.asyncio
async def test_should_not_rejoin_in_finished_room():
    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED)
    room_service = get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = first_player_id

    with pytest.raises(RoomNotJoinableError):
        await room_service.rejoin(player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid)


@pytest.mark.asyncio
async def test_should_not_rejoin_room_player_not_found():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    first_player_sid = existing_players[0].latest_sid
    existing_room.host = existing_players[0].player_id

    with pytest.raises(PlayerNotFound):
        await room_service.rejoin(
            player_service=player_service, player_id="player-id-unknown", latest_sid=first_player_sid
        )


@pytest.mark.asyncio
async def test_should_not_rejoin_room_has_no_host():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=existing_room.room_id)
    player_service = get_player_service(players=existing_players)
    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid

    with pytest.raises(RoomHasNoHostError):
        await room_service.rejoin(player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid)


@pytest.mark.asyncio
async def test_should_not_rejoin_room_not_found():
    existing_room: Room = RoomFactory.build(state=RoomState.CREATED)
    room_service = get_room_service(rooms=[existing_room])

    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id="unknown-room-id")
    player_service = get_player_service(players=existing_players)
    existing_room.host = existing_players[0].player_id

    first_player_id = existing_players[0].player_id
    first_player_sid = existing_players[0].latest_sid

    with pytest.raises(RoomNotFound):
        await room_service.rejoin(player_service=player_service, player_id=first_player_id, latest_sid=first_player_sid)


@pytest.mark.asyncio
async def test_should_get_room_players_info():
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
async def test_should_kick_player():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    player_service = get_player_service(existing_players)
    room_service = get_room_service(rooms=[existing_room])

    player_kicked = await room_service.kick_player(
        player_service=player_service,
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
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    player_service = get_player_service(existing_players)
    room_service = get_room_service(rooms=[existing_room])

    with pytest.raises(PlayerNotHostError):
        await room_service.kick_player(
            player_service=player_service,
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=existing_players[2].player_id,
            room_id=existing_room.room_id,
        )


@pytest.mark.asyncio
async def test_should_not_kick_player_room_not_found():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    player_service = get_player_service(existing_players)
    room_service = get_room_service(rooms=[existing_room])

    with pytest.raises(RoomNotFound):
        await room_service.kick_player(
            player_service=player_service,
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=room_host_player_id,
            room_id="BADROOM",
        )


@pytest.mark.asyncio
async def test_should_not_kick_player_invalid_room_state():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.FINISHED, room_id=room_id, host=room_host_player_id)
    existing_players: List[Player] = PlayerFactory.build_batch(3, room_id=room_id)
    existing_players[0].player_id = room_host_player_id
    player_to_kick = existing_players[1]

    player_service = get_player_service(existing_players)
    room_service = get_room_service(rooms=[existing_room])

    with pytest.raises(RoomInInvalidState):
        await room_service.kick_player(
            player_service=player_service,
            player_to_kick_nickname=player_to_kick.nickname,
            player_attempting_kick=room_host_player_id,
            room_id=existing_room.room_id,
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
    room_service = get_room_service(rooms=[existing_room])

    await room_service.update_host(
        player_service=player_service, room=existing_room, old_host_id=player_disconnected.player_id
    )

    room = await room_service.get(room_id=existing_room.room_id)
    assert not room.host == player_disconnected.player_id


@pytest.mark.asyncio
async def test_should_start_game(httpx_mock: HTTPXMock):
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    room_service = get_room_service(rooms=[existing_room])
    game_api = get_game_api_client()

    _mock_get_game(httpx_mock)
    room = await room_service.start_game(
        game_api=game_api, game_name="fibbing_it", room_id=existing_room.room_id, player_id=room_host_player_id
    )
    assert room.state == RoomState.PLAYING


@pytest.mark.asyncio
async def test_should_not_start_game_room_playing_game():
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.PLAYING, room_id=room_id, host=room_host_player_id)
    room_service = get_room_service(rooms=[existing_room])
    game_api = get_game_api_client()

    with pytest.raises(RoomInInvalidState):
        await room_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id=existing_room.room_id, player_id=room_host_player_id
        )


@pytest.mark.asyncio
async def test_should_start_game_game_disabled(httpx_mock: HTTPXMock):
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    room_service = get_room_service(rooms=[existing_room])
    game_api = get_game_api_client()

    _mock_get_game(httpx_mock, enabled=False)
    with pytest.raises(GameNotEnabled):
        await room_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id=existing_room.room_id, player_id=room_host_player_id
        )


@pytest.mark.asyncio
async def test_should_not_start_game_room_not_found(httpx_mock: HTTPXMock):
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    room_service = get_room_service(rooms=[existing_room])
    game_api = get_game_api_client()

    with pytest.raises(RoomNotFound):
        await room_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id="random-room-id", player_id=room_host_player_id
        )


@pytest.mark.asyncio
async def test_should_not_start_game_player_not_host(httpx_mock: HTTPXMock):
    room_id = "4d18ac45-8034-4f8e-b636-cf730b17e51a"
    room_host_player_id = "5a18ac45-9876-4f8e-b636-cf730b17e59l"

    existing_room: Room = RoomFactory.build(state=RoomState.CREATED, room_id=room_id, host=room_host_player_id)
    room_service = get_room_service(rooms=[existing_room])
    game_api = get_game_api_client()

    with pytest.raises(PlayerNotHostError):
        await room_service.start_game(
            game_api=game_api, game_name="fibbing_it", room_id=room_id, player_id="another_player_id"
        )


def _sort_list_by_player_id(players: List[Player]):
    players.sort(key=lambda p: p.player_id, reverse=True)


def _mock_get_game(httpx_mock: HTTPXMock, enabled=True):
    httpx_mock.add_response(
        url="http://localhost/game/fibbing_it",
        method="GET",
        json=GameOut(
            name="fibbing_it",
            display_name="",
            description="",
            enabled=enabled,
            minimum_players=0,
            maximum_players=10,
            rules_url="",
        ).dict(),
    )
