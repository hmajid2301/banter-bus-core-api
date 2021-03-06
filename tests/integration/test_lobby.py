import asyncio
import base64

import pytest
from socketio.asyncio_client import AsyncClient

from app.event_models import Error
from app.main import sio
from app.room.lobby.lobby_events_models import (
    GameStarted,
    JoinRoom,
    KickPlayer,
    NewRoomJoined,
    PlayerKicked,
    RoomCreated,
    RoomJoined,
    StartGame,
)


@pytest.mark.asyncio
async def test_room_created(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ROOM_CREATED")
    def _(data):
        future.set_result(RoomCreated(**data))

    await client.emit("CREATE_ROOM", {})
    await asyncio.wait_for(future, timeout=5.0)
    room_created: RoomCreated = future.result()
    assert room_created.room_code


@pytest.mark.asyncio
async def test_empty_room_joined(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ROOM_JOINED")
    def _(data):
        future.set_result(RoomJoined(**data))

    avatar = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    join_room = JoinRoom(
        avatar=avatar,
        nickname="Majiy",
        room_code="4d18ac45-8034-4f8e-b636-cf730b17e51a",
    )
    await client.emit("JOIN_ROOM", join_room.dict())
    await asyncio.wait_for(future, timeout=5.0)
    room_joined: RoomJoined = future.result()
    player = room_joined.players[0]
    assert player.nickname == join_room.nickname
    assert player.avatar == avatar


@pytest.mark.asyncio
async def test_empty_room_joined_new_room_event(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("NEW_ROOM_JOINED")
    def _(data):
        future.set_result(NewRoomJoined(**data))

    avatar = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    join_room = JoinRoom(
        avatar=avatar,
        nickname="Majiy",
        room_code="4d18ac45-8034-4f8e-b636-cf730b17e51a",
    )
    await client.emit("JOIN_ROOM", join_room.dict())
    await asyncio.wait_for(future, timeout=5.0)
    new_room_joined: NewRoomJoined = future.result()
    assert new_room_joined.player_id is not None


@pytest.mark.asyncio
async def test_room_joined_nickname_in_use(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ERROR")
    def _(data):
        future.set_result(Error(**data))

    join_room = JoinRoom(
        avatar=base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        ),
        nickname="Majiy",
        room_code="5a18ac45-9876-4f8e-b636-cf730b17e59l",
    )
    await client.emit("JOIN_ROOM", join_room.dict())
    await asyncio.wait_for(future, timeout=5.0)
    error: Error = future.result()
    assert error.code == "room_join_fail"
    assert error.message == "nickname Majiy already exists"


@pytest.mark.asyncio
async def test_kick_room(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("PLAYER_KICKED")
    def _(data):
        future.set_result(PlayerKicked(**data))

    player_to_kick_nickname = "CanIHaseeburger"
    room_code = "5a18ac45-9876-4f8e-b636-cf730b17e59l"
    kick_player = KickPlayer(
        kick_player_nickname=player_to_kick_nickname,
        player_id="52dcb730-93ad-4364-917a-8760ee50d0f5",
        room_code=room_code,
    )
    sio.enter_room(client.get_sid(), room=room_code)
    await client.emit("KICK_PLAYER", kick_player.dict())
    await asyncio.wait_for(future, timeout=5.0)
    player_kicked: PlayerKicked = future.result()
    assert player_kicked.nickname == player_to_kick_nickname


@pytest.mark.asyncio
async def test_kick_room_not_host(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ERROR")
    def _(data):
        future.set_result(Error(**data))

    player_to_kick_nickname = "Majiy"
    kick_player = KickPlayer(
        kick_player_nickname=player_to_kick_nickname,
        player_id="66dcb730-93de-4364-917a-8760ee50d0ff",
        room_code="5a18ac45-9876-4f8e-b636-cf730b17e59l",
    )
    await client.emit("KICK_PLAYER", kick_player.dict())
    await asyncio.wait_for(future, timeout=5.0)
    error: Error = future.result()
    assert error.code == "kick_player_fail"
    assert error.message == "You are not host, so cannot kick another player"


@pytest.mark.asyncio
async def test_start_game(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("GAME_STARTED")
    def _(data):
        future.set_result(GameStarted(**data))

    room_code = "5a18ac45-9876-4f8e-b636-cf730b17e59l"
    start_game = StartGame(
        game_name="fibbing_it",
        room_code=room_code,
        player_id="52dcb730-93ad-4364-917a-8760ee50d0f5",
    )
    sio.enter_room(client.get_sid(), room=room_code)
    await client.emit("START_GAME", start_game.dict())
    await asyncio.wait_for(future, timeout=5.0)
    game_started: GameStarted = future.result()
    assert game_started.game_name == "fibbing_it"
