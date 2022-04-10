from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.clients.management_api.api_client import ApiClient
from app.core.config import get_settings
from app.game_state.game_state_repository import (
    AbstractGameStateRepository,
    GameStateRepository,
)
from app.game_state.game_state_service import GameStateService


def get_question_api() -> AsyncQuestionsApi:
    settings = get_settings()
    api_host = settings.get_management_url()
    api_client = ApiClient(host=api_host)

    question_api_client = AsyncQuestionsApi(api_client=api_client)
    return question_api_client


def get_game_state_repository() -> AbstractGameStateRepository:
    return GameStateRepository()


def get_game_state_service() -> GameStateService:
    question_api_client = get_question_api()
    game_state_repository = get_game_state_repository()
    game_state_service = GameStateService(
        game_state_repository=game_state_repository, question_client=question_api_client
    )
    return game_state_service
