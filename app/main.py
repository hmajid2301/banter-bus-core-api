from fastapi import FastAPI
from fastapi_socketio import SocketManager
from omnibus.app import setup_app

from app.core.config import get_settings
from app.healthcheck import db_healthcheck
from app.player.player_models import Player
from app.room.room_models import Room

application = FastAPI(title="banter-bus-core-api")
sio = SocketManager(app=application, mount_location="/")


@application.on_event("startup")
async def startup():
    await setup_app(
        app=application, get_settings=get_settings, document_models=[Room, Player], healthcheck=db_healthcheck
    )
