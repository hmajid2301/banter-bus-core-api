import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_disconnect_players(http: AsyncClient):
    response = await http.put("/player:disconnect")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "disconnected_players": [
            "778cb730-93de-4364-917a-8760ee50d0ff",
            "8760ee50d0ff-93de-4364-917a-778cb730",
        ],
    }
