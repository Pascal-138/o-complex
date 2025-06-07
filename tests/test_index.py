import pytest


@pytest.mark.asyncio
async def test_index_page(client):
    response = await client.get("/")
    assert response.status_code == 200
