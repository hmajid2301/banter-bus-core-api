import httpx
from pytest_httpx import HTTPXMock

from app.clients.management_api.models import GameOut
from tests.unit.data.http_requests import get_questions_mock_data


def mock_get_questions(httpx_mock: HTTPXMock):
    def custom_response(request: httpx.Request):
        return httpx.Response(
            status_code=200,
            json=get_questions_mock_data[str(request.url)],
        )

    httpx_mock.add_callback(custom_response, method="GET")


def mock_get_game(httpx_mock: HTTPXMock, enabled=True):
    httpx_mock.add_response(
        url="http://localhost/game/fibbing_it",
        method="GET",
        json=GameOut(
            name="fibbing_it",
            display_name="",
            description="",
            enabled=enabled,
            minimum_players=1,
            maximum_players=10,
            rules_url="",
        ).dict(),
    )
