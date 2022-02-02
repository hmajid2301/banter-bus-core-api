from fastapi import FastAPI
from fastapi_socketio import SocketManager
from omnibus.app import setup_app
from omnibus.operation_id import use_route_names_as_operation_ids

from app.core.config import get_settings
from app.core.exception_handlers import log_uncaught_exceptions
from app.healthcheck import db_healthcheck
from app.player import player_api
from app.player.player_models import Player
from app.room.room_models import Room

app = FastAPI(title="banter-bus-core-api")
sio = SocketManager(app=app)


@app.on_event("startup")
async def startup():
    await setup_app(app=app, get_settings=get_settings, document_models=[Room, Player], healthcheck=db_healthcheck)
    app.add_exception_handler(Exception, log_uncaught_exceptions)
    app.include_router(player_api.router)
    use_route_names_as_operation_ids(app)
