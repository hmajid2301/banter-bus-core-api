from typing import List

from fastapi import APIRouter, Depends, status
from omnibus.log.logger import get_logger
from structlog import BoundLogger

from app.core.config import get_settings
from app.player.player_api_models import DisconnectPlayers
from app.player.player_factory import get_player_service
from app.player.player_service import PlayerService

router = APIRouter(
    prefix="/player",
    tags=["players"],
)


@router.put(":disconnect", status_code=status.HTTP_200_OK, response_model=DisconnectPlayers)
async def disconnect_players(
    player_service: PlayerService = Depends(get_player_service),
    logger: BoundLogger = Depends(get_logger),
):

    logger.debug("trying to disconnect players")
    config = get_settings()
    disconnected_players = await player_service.disconnect_players(
        disconnect_timer_in_minutes=config.DISCONNECT_TIMER_IN_MINUTES
    )

    disconnected_player_ids: List[str] = [player.player_id for player in disconnected_players]
    logger.debug("disconnected players", players=disconnected_players)
    return DisconnectPlayers(disconnected_players=disconnected_player_ids)
