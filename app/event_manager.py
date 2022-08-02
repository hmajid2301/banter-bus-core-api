from collections.abc import Callable, Coroutine
from typing import Any

from structlog import get_logger

from app.core.config import get_settings
from app.event_models import ERROR, Error
from app.main import sio
from app.room.room_events_models import EventModel, EventResponse


def error_handler(exception: type[Exception], error_callback: Callable[[str], Coroutine[Any, Any, None]]):
    def outer(func: Callable[[str, Any], Coroutine[Any, Any, Any]]):  # TODO alias these complicated types
        async def inner(sid: str, data: EventModel):
            try:
                return await func(sid, data)
            except exception:
                return await error_callback(sid)

        return inner

    return outer


def event_handler(input_model: type[EventModel]):
    def outer(func: Callable[[str, Any], Coroutine[Any, Any, tuple[list[EventResponse] | EventModel, str | None]]]):
        async def inner(sid: str, data: dict[Any, Any]):
            model = input_model(**data)  # type: ignore

            logger = get_logger()
            logger.debug(model.event_name)

            response, room = await func(sid, model)
            if isinstance(response, Error):
                await sio.emit(ERROR, response.dict(), room=room)
            else:
                if isinstance(response, list) and isinstance(response[0], EventResponse):
                    for r in response:
                        await sio.emit(r.response_data.event_name, r.response_data.dict(), room=r.send_to)
                        _log_resonse(r.response_data)
                elif isinstance(response, EventModel):
                    await sio.emit(response.event_name, response.dict(), room=room)
                    _log_resonse(response)

        def _log_resonse(response: EventModel):
            exclude = {}
            settings = get_settings()
            for attribute, ignore_fields in settings.LOG_RESPONSE_EXCLUDE_ATTR["list"].items():
                if hasattr(response, attribute):
                    list_ = len(getattr(response, attribute))
                    exclude_index = {index: ignore_fields for index in range(list_)}
                    exclude[attribute] = exclude_index

            logger = get_logger()
            logger.debug(response.event_name, data=response.dict(exclude=exclude))

        return inner

    return outer


async def publish_event(event_name: str, event_body: EventModel, room: str | None = None):
    await sio.emit(event_name, event_body.dict(), room=room)


def enter_room(sid: str, room: str):
    sio.enter_room(sid, room)


def leave_room(sid: str, room: str):
    sio.leave_room(sid, room)
