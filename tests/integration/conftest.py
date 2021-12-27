import asyncio
from typing import Any, AsyncIterator, Awaitable, List, Optional

import pytest
import socketio
import uvicorn
from fastapi.applications import FastAPI
from socketio.asyncio_client import AsyncClient

from app import application

PORT = 8000
LISTENING_IF = "127.0.0.1"
BASE_URL = f"http://{LISTENING_IF}:{PORT}"


class UvicornTestServer(uvicorn.Server):
    def __init__(self, app: FastAPI = application, host: str = LISTENING_IF, port: int = PORT):
        self._startup_done = asyncio.Event()
        self._serve_task: Optional[Awaitable[Any]] = None
        super().__init__(config=uvicorn.Config(app, host=host, port=port))

    async def startup(self, sockets: Optional[List] = None) -> None:
        await super().startup(sockets=sockets)
        self.config.setup_event_loop()
        self._startup_done.set()

    async def start_up(self) -> None:
        self._serve_task = asyncio.create_task(self.serve())
        await self._startup_done.wait()

    async def tear_down(self) -> None:
        self.should_exit = True
        if self._serve_task:
            await self._serve_task


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def startup_and_shutdown_server():
    server = UvicornTestServer()
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
    from app.room.room_models import Room
    from tests.data.room_collection import rooms

    try:
        await Room.insert_many(documents=rooms)
    except Exception as e:
        print("Failed", e)
    yield
    await Room.delete_all()
