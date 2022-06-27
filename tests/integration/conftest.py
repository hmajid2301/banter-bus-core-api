import asyncio
from typing import AsyncIterator

import pytest
import socketio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient as HttpXClient
from omnibus.tests.uvicorn_test_server import UvicornTestServer
from socketio.asyncio_client import AsyncClient

from app import app  # type: ignore
from app.game_state.game_state_models import GameState

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
    await sio.connect(BASE_URL, socketio_path="/ws/socket.io")
    yield sio
    await sio.disconnect()


# TODO: refactor repeated code
@pytest.fixture(scope="session")
async def client_two() -> AsyncIterator[AsyncClient]:
    sio = socketio.AsyncClient()
    await sio.connect(BASE_URL, socketio_path="/ws/socket.io")
    yield sio
    await sio.disconnect()


@pytest.fixture()
async def http() -> AsyncIterator[HttpXClient]:
    async with LifespanManager(app):
        async with HttpXClient(app=app, base_url="http://localhost") as client:
            yield client


@pytest.fixture(autouse=True, scope="function")
async def setup_and_teardown(startup_and_shutdown_server, http):
    from app.player.player_models import Player
    from app.room.room_models import Room
    from tests.data.game_state_collection import game_states
    from tests.data.player_collection import players
    from tests.data.room_collection import rooms

    try:
        await Room.insert_many(documents=rooms)
        await Player.insert_many(documents=players)
        await GameState.insert_many(documents=game_states)
    except Exception as e:
        print("Failed", e)
    yield
    await Room.delete_all()
    await Player.delete_all()
    await GameState.delete_all()
