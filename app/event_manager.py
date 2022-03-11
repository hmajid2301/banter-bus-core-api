from typing import Any, Callable, Coroutine, Optional, Type

from structlog import get_logger

from app.main import sio
from app.room.room_events_models import ERROR, Error, EventModel


def error_handler(exception: Type[Exception], error_callback: Callable[[str], Coroutine[Any, Any, None]]):
    def outer(func: Callable[[str, Any], Coroutine[Any, Any, Any]]):  # TODO alias these complicated types
        async def inner(sid: str, data: EventModel):
            try:
                return await func(sid, data)
            except exception:
                return await error_callback(sid)

        return inner

    return outer


def event_handler(input_model: Type[EventModel]):
    def outer(func: Callable[[str, Any], Coroutine[Any, Any, Any]]):
        async def inner(sid: str, data: dict):
            model = input_model(**data)

            logger = get_logger()
            logger.debug(model.event_name)

            response, room = await func(sid, model)
            if isinstance(response, Error):
                await sio.emit(ERROR, response.dict(), room=room)
            else:
                await sio.emit(response.event_name, response.dict(), room=room)
                logger.debug(response.event_name, data=response.dict())

        return inner

    return outer


async def publish_event(event_name: str, event_body: EventModel, room: Optional[str] = None):
    await sio.emit(event_name, event_body.dict(), room=room)


def enter_room(sid: str, room: str):
    sio.enter_room(sid, room)


def leave_room(sid: str, room: str):
    sio.leave_room(sid, room)
