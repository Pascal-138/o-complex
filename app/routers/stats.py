from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_session
from app.db.models import SearchHistory

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"]
)


@router.get("/city-usage")
async def city_usage(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(SearchHistory.city, func.count(SearchHistory.city))
        .group_by(SearchHistory.city)
        .order_by(func.count(SearchHistory.city).desc())
    )
    city_counts = result.all()
    return {"city_usage":
            [{"city": city, "count": count} for city, count in city_counts]}
