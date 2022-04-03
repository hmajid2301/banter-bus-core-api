from app.player.player_repository import AbstractPlayerRepository, PlayerRepository
from app.player.player_service import PlayerService


def get_player_repository() -> AbstractPlayerRepository:
    return PlayerRepository()


def get_player_service() -> PlayerService:
    player_repository = get_player_repository()
    player_service = PlayerService(game_state_repository=player_repository)
    return player_service
