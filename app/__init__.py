import uvicorn

import app.room.room_event_handlers  # noqa
from app.core.config import get_settings
from app.main import app as application

app = application  # noqa

if __name__ == "__main__":
    config = get_settings()
    uvicorn.run(app, host=config.WEB_HOST, port=config.WEB_PORT)  # type: ignore
