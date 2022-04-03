import httpx
from pytest_httpx import HTTPXMock

from tests.unit.data.http_requests import get_questions_mock_data


def mock_get_questions(httpx_mock: HTTPXMock):
    def custom_response(request: httpx.Request):
        return httpx.Response(
            status_code=200,
            json=get_questions_mock_data[str(request.url)],
        )

    httpx_mock.add_callback(custom_response, method="GET")
