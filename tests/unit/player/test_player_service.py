from datetime import datetime, timedelta
from typing import List

import pytest
from pytest_mock import MockFixture

from app.player.player_exceptions import PlayerNotFound
from app.player.player_models import Player
from app.player.player_service import PlayerService
from tests.unit.factories import PlayerFactory, get_new_player
from tests.unit.player.fake_player_repository import FakePlayerRepository


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_create_player():
    player_repository = FakePlayerRepository(players=[])
    player_service = PlayerService(player_repository=player_repository)
    room_id = "b6add44d-0e9b-4a27-93c6-c9a8be88575b"

    new_player = get_new_player()

    player = await player_service.create(room_id=room_id, new_player=new_player)
    expected_player = Player(**new_player.dict(), room_id=room_id, player_id=player.player_id)
    assert player == expected_player


@pytest.mark.asyncio
async def test_get_player():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    first_player = existing_players[0]
    player = await player_service.get(player_id=first_player.player_id)
    assert player == existing_players[0]


@pytest.mark.asyncio
async def test_get_player_not_found():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    with pytest.raises(PlayerNotFound):
        await player_service.get(player_id="unknown-id")


@pytest.mark.asyncio
async def test_get_all_in_room():
    room_id = "b6add44d-0e9b-4a27-93c6-c9a8be88575b"
    existing_players = PlayerFactory.build_batch(3, room_id=room_id)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    players = await player_service.get_all_in_room(room_id=room_id)
    assert players == existing_players


@pytest.mark.asyncio
async def test_get_all_in_room_no_players():
    room_id = "b6add44d-0e9b-4a27-93c6-c9a8be88575b"
    existing_players = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    players = await player_service.get_all_in_room(room_id=room_id)
    assert players == []


@pytest.mark.asyncio
async def test_remove_room():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    first_player = existing_players[0]
    player = await player_service.remove_from_room(nickname=first_player.nickname, room_id=first_player.room_id or "")
    assert player.room_id is None


@pytest.mark.asyncio
async def test_remove_room_player_not_found():
    player_repository = FakePlayerRepository(players=[])
    player_service = PlayerService(player_repository=player_repository)

    with pytest.raises(PlayerNotFound):
        await player_service.remove_from_room(nickname="random_nickname", room_id="not_found")


@pytest.mark.asyncio
async def test_update_disconnected_time():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    first_player = existing_players[0]
    player = await player_service.update_disconnected_time(sid=first_player.latest_sid)
    assert player.disconnected_at is not None


@pytest.mark.asyncio
async def test_update_latest_sid():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    first_player = existing_players[0]
    new_sid = "123456789"
    player = await player_service.update_latest_sid(player=first_player, latest_sid=new_sid)
    assert player.latest_sid == new_sid


@pytest.mark.asyncio
async def test_disconnect_players():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    first_player = existing_players[0]
    first_player.disconnected_at = datetime.now() - timedelta(minutes=5)
    player = await player_service.disconnect_player(
        nickname=first_player.nickname, room_id=first_player.room_id, disconnect_timer_in_seconds=300
    )
    assert player.room_id is None


@pytest.mark.asyncio
async def test_disconnect_players_less_than_5_mins():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    first_player = existing_players[0]
    first_player.disconnected_at = datetime.now() - timedelta(minutes=3)
    player = await player_service.disconnect_player(
        nickname=first_player.nickname, room_id=first_player.room_id, disconnect_timer_in_seconds=300
    )
    assert player.room_id is not None


@pytest.mark.asyncio
async def test_disconnect_players_not_found():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_repository = FakePlayerRepository(players=existing_players)
    player_service = PlayerService(player_repository=player_repository)

    first_player = existing_players[0]
    with pytest.raises(PlayerNotFound):
        await player_service.disconnect_player(
            nickname=first_player.nickname, room_id="room-id_not_found", disconnect_timer_in_seconds=300
        )
