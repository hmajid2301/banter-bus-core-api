import pytest
from fastapi import status
from httpx import AsyncClient

from app.story.story_models import Story
from tests.integration.data.story_test_data import (
    add_story_data,
    delete_story_data,
    get_story_data,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_data, expected_status_code, expected_result",
    add_story_data,
    ids=[
        "add a quibly story",
        "add a fibbing_it story",
        "try to add a story (game not found)",
        "try to add a story (missing game_name)",
        "try to add a quibly story (invalid round)",
        "try to add a quibly story (missing round)",
        "try to add a quibly story (missing Story)",
        "try to add a quibly story (missing answer)",
        "try to add a quibly story (unexpected nickname)",
        "try to add a drawlosseum story (missing nickname)",
        "try to add a fibbing_it story (invalid round)",
        "try to add a fibbing_it story (missing Story)",
        "try to add a fibbing_it story (missing round)",
        "try to add a fibbing_it story (unexpected nickname)",
    ],
)
async def test_add_story(client: AsyncClient, request_data: dict, expected_status_code: int, expected_result: dict):
    response = await client.post("/story", json=request_data)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_201_CREATED:
        clean_response = _clean_response(response.json())
        assert clean_response == expected_result


def _clean_response(response: dict):
    del response["story_id"]
    return response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "story_id, expected_status_code, expected_result",
    get_story_data,
    ids=[
        "get a quibly story",
        "get a drawlosseum story",
        "try to get a story that does not exist",
    ],
)
async def test_get_story(client: AsyncClient, story_id: str, expected_status_code: int, expected_result: dict):
    url = f"/story/{story_id}"
    response = await client.get(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        assert response.json() == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "story_id, expected_status_code",
    delete_story_data,
    ids=[
        "delete a quibly story",
        "delete a drawlosseum story",
        "try to delete a story that does not exist",
    ],
)
async def test_delete_story(client: AsyncClient, story_id: str, expected_status_code: int):
    url = f"/story/{story_id}"
    response = await client.delete(url)
    assert response.status_code == expected_status_code

    if response.status_code == status.HTTP_200_OK:
        story = await Story.find_one(Story.story_id == story_id)
        assert story is None
