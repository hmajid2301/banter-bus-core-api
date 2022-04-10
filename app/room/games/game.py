from app.core.exceptions import GameNotFound
from app.room.games.abstract_game import AbstractGame
from app.room.games.fibbing_it import FibbingIt


def get_game(game_name: str) -> AbstractGame:
    if game_name == "fibbing_it":
        return FibbingIt()
    else:
        raise GameNotFound(f"game {game_name} not found")
