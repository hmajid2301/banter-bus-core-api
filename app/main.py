from fastapi import FastAPI
from omnibus.app import setup_app
from omnibus.log.logger import get_logger
from omnibus.operation_id import use_route_names_as_operation_ids

from app.core.config import get_settings
from app.core.exception_handlers import log_uncaught_exceptions
from app.game_state.game_state_models import GameState
from app.healthcheck import db_healthcheck
from app.player.player_models import Player
from app.room.room_models import Room
from app.socket_manager import SocketManager

application = FastAPI(title="banter-bus-core-api")
sio = SocketManager(app=application, redis_uri=get_settings().get_redis_uri())


@application.on_event("startup")
async def startup():
    await setup_app(
        app=application,
        get_settings=get_settings,
        document_models=[Room, Player, GameState],
        healthcheck=db_healthcheck,
    )
    application.add_exception_handler(Exception, log_uncaught_exceptions)
    use_route_names_as_operation_ids(application)
    log = get_logger()
    log.info("TESTIng")
