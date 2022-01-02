import asyncio
import base64
import re

import pytest
from socketio.asyncio_client import AsyncClient

from app.room.room_events_models import (
    CreateRoom,
    Error,
    JoinRoom,
    RoomCreated,
    RoomJoined,
)


@pytest.mark.asyncio
async def test_room_created(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ROOM_CREATED")
    def _(data):
        future.set_result(RoomCreated(**data))

    create_room = CreateRoom(
        game_name="fibbing_it",
    )
    await client.emit("CREATE_ROOM", create_room.dict())
    await asyncio.wait_for(future, timeout=5.0)
    room_created: RoomCreated = future.result()
    assert re.match(r"^[A-Z]{0,5}$", room_created.room_code)


@pytest.mark.asyncio
async def test_room_created_game_not_enabled(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ERROR")
    def _(data):
        future.set_result(Error(**data))

    create_room = CreateRoom(
        game_name="quibly",
    )
    await client.emit("CREATE_ROOM", create_room.dict())
    await asyncio.wait_for(future, timeout=1.0)
    err: Error = future.result()
    assert err.code == "room_create_fail"


@pytest.mark.asyncio
async def test_empty_room_joined(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ROOM_JOINED")
    def _(data):
        future.set_result(RoomJoined(**data))

    join_room = JoinRoom(
        avatar=base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        ),
        nickname="Majiy",
        room_code="ABCDE",
    )
    await client.emit("JOIN_ROOM", join_room.dict())
    await asyncio.wait_for(future, timeout=5.0)
    room_joined: RoomJoined = future.result()
    player = room_joined.players[0]
    assert player.nickname == join_room.nickname
    assert player.avatar == join_room.avatar


@pytest.mark.asyncio
async def test_joined_nickname(client: AsyncClient):
    future = asyncio.get_running_loop().create_future()

    @client.on("ERROR")
    def _(data):
        future.set_result(Error(**data))

    join_room = JoinRoom(
        avatar=base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        ),
        nickname="Majiy",
        room_code="BCDEF",
    )
    await client.emit("JOIN_ROOM", join_room.dict())
    await asyncio.wait_for(future, timeout=5.0)
    error: Error = future.result()
    assert error.code == "room_join_fail"
    assert error.message == "nickname Majiy already exists"
