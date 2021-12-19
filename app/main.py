import logging

import socketio
import uvicorn
from beanie import init_beanie
from motor import motor_asyncio

from app.core.config import get_settings
from app.core.logger import get_logger, setup_logger
from app.room.room_event_handlers import create_room
from app.room.room_events_models import CreateRoom, Error
from app.room.room_models import Room

logger = logging.getLogger()


async def startup():
    config = get_settings()
    setup_logger(config.LOG_LEVEL)
    uri = config.get_mongodb_uri()
    client = motor_asyncio.AsyncIOMotorClient(uri)
    await init_beanie(database=client[config.DB_NAME], document_models=[Room])
    log = get_logger()
    log.info(f"starting banter-bus-core-api {config.WEB_HOST}:{config.WEB_PORT}")


sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio, on_startup=startup)


@sio.on("CREATE_ROOM")
async def create_room_event(sid, *args, **kwargs):
    create_room_data = CreateRoom(**args[0])
    logger = get_logger()
    logger.debug("creating room")
    try:
        room_created = await create_room(create_room_data=create_room_data)
        await sio.emit("ROOM_CREATED", room_created.dict())
        logger.debug("room created", room_created=room_created.dict())
    except Exception:
        logger.exception("failed to create room")
        error = Error(code="room_create_fail", message="failed to create room")
        await sio.emit("ERROR", error.dict())


# TODO: sent error middleware


if __name__ == "__main__":
    config = get_settings()
    uvicorn.run(app, host=config.WEB_HOST, port=config.WEB_PORT)  # type: ignore
