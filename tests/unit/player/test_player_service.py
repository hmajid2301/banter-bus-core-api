from datetime import datetime, timedelta
from typing import List

import pytest
from pytest_mock import MockFixture

from app.player.player_exceptions import PlayerNotFound
from app.player.player_models import Player
from tests.unit.factories import PlayerFactory, get_new_player
from tests.unit.get_services import get_player_service


@pytest.fixture(autouse=True)
def mock_beanie_document(mocker: MockFixture):
    mocker.patch("beanie.odm.documents.Document.get_settings")


@pytest.mark.asyncio
async def test_should_create_new_player():
    player_service = get_player_service()

    room_id = "b6add44d-0e9b-4a27-93c6-c9a8be88575b"
    new_player = get_new_player()

    player = await player_service.create(room_id=room_id, new_player=new_player)
    expected_player = Player(**new_player.dict(), room_id=room_id, player_id=player.player_id)
    assert player == expected_player


@pytest.mark.asyncio
async def test_should_get_player():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_service = get_player_service(players=existing_players)

    first_player = existing_players[0]
    player = await player_service.get(player_id=first_player.player_id)
    assert player == existing_players[0]


@pytest.mark.asyncio
async def test_should_not_get_player():
    player_service = get_player_service(num=3)

    with pytest.raises(PlayerNotFound):
        await player_service.get(player_id="unknown-id")


@pytest.mark.asyncio
async def test_should_get_all_players_in_room():
    room_id = "b6add44d-0e9b-4a27-93c6-c9a8be88575b"
    existing_players = PlayerFactory.build_batch(3, room_id=room_id)
    player_service = get_player_service(players=existing_players)

    players = await player_service.get_all_in_room(room_id=room_id)
    assert players == existing_players


@pytest.mark.asyncio
async def test_should_get_no_players_in_room():
    player_service = get_player_service()

    room_id = "b6add44d-0e9b-4a27-93c6-c9a8be88575b"
    players = await player_service.get_all_in_room(room_id=room_id)
    assert players == []


@pytest.mark.asyncio
async def test_should_remove_player_from_room():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_service = get_player_service(players=existing_players)

    first_player = existing_players[0]
    player = await player_service.remove_from_room(nickname=first_player.nickname, room_id=first_player.room_id or "")
    assert player.room_id is None


@pytest.mark.asyncio
async def test_should_not_remove_player_from_room():
    player_service = get_player_service(players=[])

    with pytest.raises(PlayerNotFound):
        await player_service.remove_from_room(nickname="random_nickname", room_id="not_found")


@pytest.mark.asyncio
async def test_should_update_disconnected_at_time():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_service = get_player_service(players=existing_players)

    first_player = existing_players[0]
    player = await player_service.update_disconnected_time(player=first_player, disconnected_at=datetime.now())
    assert player.disconnected_at is not None


@pytest.mark.asyncio
async def test_should_update_sid():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_service = get_player_service(players=existing_players)

    first_player = existing_players[0]
    new_sid = "123456789"
    player = await player_service.update_latest_sid(player=first_player, latest_sid=new_sid)
    assert player.latest_sid == new_sid


@pytest.mark.asyncio
async def test_player_gets_disconnected():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_service = get_player_service(players=existing_players)

    first_player = existing_players[0]
    first_player.disconnected_at = datetime.now() - timedelta(minutes=5)
    player = await player_service.disconnect_player(
        nickname=first_player.nickname, room_id=first_player.room_id, disconnect_timer_in_seconds=300
    )
    assert player.room_id is None


@pytest.mark.asyncio
async def test_should_not_disconnect_player_under_five_minutes():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_service = get_player_service(players=existing_players)

    first_player = existing_players[0]
    first_player.disconnected_at = datetime.now() - timedelta(minutes=3)
    player = await player_service.disconnect_player(
        nickname=first_player.nickname, room_id=first_player.room_id, disconnect_timer_in_seconds=300
    )
    assert player.room_id is not None


@pytest.mark.asyncio
async def test_should_not_disconnect_player_not_found():
    existing_players: List[Player] = PlayerFactory.build_batch(3)
    player_service = get_player_service(players=existing_players)

    first_player = existing_players[0]
    with pytest.raises(PlayerNotFound):
        await player_service.disconnect_player(
            nickname=first_player.nickname, room_id="room-id_not_found", disconnect_timer_in_seconds=300
        )
