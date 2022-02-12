import asyncio
import base64

import pytest
from socketio.asyncio_client import AsyncClient

from app.main import sio
from app.player.player_factory import get_player_service
from app.room.room_events_models import (
    Error,
    HostDisconnected,
    JoinRoom,
    KickPlayer,
    NewRoomJoined,
    PlayerDisconnected,
    PlayerKicked,
    RejoinRoom,
    RoomCreated,
    RoomJoined,
)
from tests.integration.conftest import BASE_URL


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
async def test_rejoin_room(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ROOM_JOINED")
    def _(data):
        future.set_result(RoomJoined(**data))

    join_room = RejoinRoom(player_id="52dcb730-93ad-4364-917a-8760ee50d0f5")
    await client.emit("REJOIN_ROOM", join_room.dict())
    await asyncio.wait_for(future, timeout=5.0)

    room_joined: RoomJoined = future.result()
    avatar = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg"
    nickname = "Majiy"
    player = room_joined.players[0]
    assert player.nickname == nickname
    assert player.avatar == avatar


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
    kick_player = KickPlayer(
        kick_player_nickname=player_to_kick_nickname,
        player_id="52dcb730-93ad-4364-917a-8760ee50d0f5",
        room_code="5a18ac45-9876-4f8e-b636-cf730b17e59l",
    )
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
async def test_disconnect(client: AsyncClient, client_two: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_service = get_player_service()
    player = await player_service.get(player_id="778cb730-93de-4364-917a-8760ee50d0ff")
    sio.enter_room(client_two.get_sid(), room=player.room_id)
    await player_service.update_latest_sid(player=player, latest_sid=client.get_sid())

    @client_two.on("PLAYER_DISCONNECTED")
    def _(data):
        future.set_result(PlayerDisconnected(**data))

    await client.disconnect()
    await asyncio.wait_for(future, timeout=5.0)

    player_disconnected_nickname = player.nickname
    player_disconnected: PlayerDisconnected = future.result()
    assert player_disconnected.nickname == player_disconnected_nickname
    sio.leave_room(client_two.get_sid(), room=player.room_id)
    await client.connect(BASE_URL, socketio_path="/ws/socket.io")


@pytest.mark.asyncio
async def test_disconnect_host(client: AsyncClient, client_two: AsyncClient):
    future = asyncio.get_running_loop().create_future()
    player_service = get_player_service()
    player = await player_service.get(player_id="52dcb730-93ad-4364-917a-8760ee50d0f5")
    sio.enter_room(client_two.get_sid(), room=player.room_id)
    await player_service.update_latest_sid(player=player, latest_sid=client.get_sid())

    @client_two.on("HOST_DISCONNECTED")
    def _(data):
        future.set_result(HostDisconnected(**data))

    await client.disconnect()
    await asyncio.wait_for(future, timeout=5.0)

    new_host_nickname = "CanIHaseeburger"
    host_disconnected: HostDisconnected = future.result()
    assert host_disconnected.new_host_nickname == new_host_nickname
    sio.leave_room(client_two.get_sid(), room=player.room_id)
    await client.connect(BASE_URL, socketio_path="/ws/socket.io")
