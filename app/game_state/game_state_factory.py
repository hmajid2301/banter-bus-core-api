from app.clients.management_api.api.questions_api import AsyncQuestionsApi
from app.clients.management_api.api_client import ApiClient
from app.core.config import get_settings


def get_question_api() -> AsyncQuestionsApi:
    settings = get_settings()
    api_host = settings.get_management_url()
    api_client = ApiClient(host=api_host)

    question_api_client = AsyncQuestionsApi(api_client=api_client)
    return question_api_client
