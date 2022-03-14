from omnibus.log.logger import get_logger

from app.event_manager import publish_event
from app.event_models import ERROR, Error


async def handle_error(sid: str):
    logger = get_logger()
    logger.exception("Failed action")
    error = Error(code="server_error", message="An unexpected error occurred on the server")
    await publish_event(event_name=ERROR, event_body=error, room=sid)
