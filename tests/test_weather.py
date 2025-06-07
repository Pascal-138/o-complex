import pytest
from app.db.models import SearchHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


@pytest.mark.asyncio
async def test_weather_creates_search_history(client,
                                              async_session: AsyncSession):
    city = "Moscow"

    response = await client.get("/weather", params={"city": city})
    assert response.status_code == 200
    await async_session.commit()

    result = await async_session.execute(
        select(SearchHistory).where(SearchHistory.city == city)
    )

    entries = result.scalars().all()
    assert entries
