from app.core.config import get_settings
from app.game_state.games.abstract_game import AbstractGame
from app.game_state.games.exceptions import GameNotFound
from app.game_state.games.fibbing_it import FibbingIt


def get_game(game_name: str) -> AbstractGame:
    settings = get_settings()

    if game_name == "fibbing_it":
        return FibbingIt(questions_per_round=settings.QUESTIONS_PER_ROUND)
    else:
        raise GameNotFound(f"game {game_name} not found")
