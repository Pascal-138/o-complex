import httpx

GEOCODE_API = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"


async def get_coordinates(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(GEOCODE_API, params={
            "name": city, "count": 1, "language": "en", "format": "json"})
        data = response.json()

    if not data.get("results"):
        return None
    result = data["results"][0]
    return result["latitude"], result["longitude"], result["name"]


async def get_weather_forecast(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "windspeed_10m_max",
            "weathercode"
        ],
        "current_weather": True,
        "timezone": "auto"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
