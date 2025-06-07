from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Query, Request, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import SearchHistory
from app.services.weather_codes import WEATHER_CODES
from app.services.weather_service import get_coordinates, get_weather_forecast


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request,
                last_city: Optional[str] = Cookie(default=None),
                session: AsyncSession = Depends(get_session)):
    ip_address = request.client.host

    result = await session.execute(
        select(SearchHistory)
        .where(SearchHistory.ip_address == ip_address)
        .order_by(SearchHistory.timestamp.desc())
        .limit(10)
    )
    history = result.scalars().all()

    stats_result = await session.execute(
        select(SearchHistory.city, func.count())
        .group_by(SearchHistory.city)
        .order_by(func.count().desc())
        .limit(5)
    )
    popular_cities = stats_result.all()

    return templates.TemplateResponse("form.html", {
        "request": request,
        "suggested_city": last_city,
        "history": history,
        "popular_cities": popular_cities
    })


@router.get("/weather", response_class=HTMLResponse)
async def get_weather(
    request: Request,
    city: str = Query(..., min_length=2),
    session: AsyncSession = Depends(get_session)
):
    coord = await get_coordinates(city)
    if not coord:
        return templates.TemplateResponse("form.html", {
            "request": request,
            "error": "Город не найден"
        })

    lat, lon, resolved_name = coord
    weather_data = await get_weather_forecast(lat, lon)

    daily = weather_data.get("daily", {})
    daily_forecast = []
    for i in range(len(daily.get("time", []))):
        daily_forecast.append({
            "date": daily["time"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "temp_max": daily["temperature_2m_max"][i],
            "wind": daily["windspeed_10m_max"][i],
            "weather": WEATHER_CODES.get(daily["weathercode"][i], "Неизвестно")
        })

    session.add(SearchHistory(
        city=resolved_name,
        ip_address=request.client.host,
        timestamp=datetime.now(timezone.utc)
    ))
    await session.commit()

    response = templates.TemplateResponse("weather.html", {
        "request": request,
        "city": resolved_name,
        "current_weather": weather_data.get("current_weather"),
        "daily_forecast": daily_forecast,
    })
    response.set_cookie(key="last_city",
                        value=resolved_name, max_age=60 * 60 * 24 * 30)

    return response


@router.get("/api/suggest_cities", response_class=JSONResponse)
async def suggest_cities(q: str = Query(..., min_length=1)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 5, "addressdetails": 1}
        )
        data = response.json()

    cities = []
    for item in data:
        if "address" in item and "city" in item["address"]:
            cities.append(item["address"]["city"])
        elif "display_name" in item:
            cities.append(item["display_name"])

    return list(set(cities))
