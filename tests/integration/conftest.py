import asyncio
from typing import AsyncIterator

import pytest
import socketio
from omnibus.tests.uvicorn_test_server import UvicornTestServer
from socketio.asyncio_client import AsyncClient

from app import app

HOST = "127.0.0.1"
PORT = 8000

BASE_URL = f"http://{HOST}:{PORT}"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def startup_and_shutdown_server():
    server = UvicornTestServer(app=app, host=HOST, port=PORT)
    await server.start_up()
    yield
    await server.tear_down()


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[AsyncClient]:
    sio = socketio.AsyncClient()
    await sio.connect(BASE_URL)
    yield sio
    await sio.disconnect()


@pytest.fixture(autouse=True)
async def setup_and_teardown(startup_and_shutdown_server):
    from app.player.player_models import Player
    from app.room.room_models import Room
    from tests.data.player_collection import players
    from tests.data.room_collection import rooms

    try:
        await Room.insert_many(documents=rooms)
        await Player.insert_many(documents=players)
    except Exception as e:
        print("Failed", e)
    yield
    await Room.delete_all()
    await Player.delete_all()
