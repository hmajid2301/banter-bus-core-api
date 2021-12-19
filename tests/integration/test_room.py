import asyncio
import re

import pytest
from socketio.asyncio_client import AsyncClient

from app.room.room_events_models import CreateRoom, Error, RoomCreated


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
