"""Weather data ingestion for prediction models."""

import httpx
from datetime import datetime
from app.config import WEATHER_API_KEY, WEATHER_BASE_URL, logger


async def get_current_weather(lat: float, lon: float) -> dict:
    """Fetch current weather for a location."""
    if not WEATHER_API_KEY:
        logger.warning("No WEATHER_API_KEY configured — returning mock data")
        return _mock_weather()
    url = f"{WEATHER_BASE_URL}/weather"
    params = {"lat": lat, "lon": lon, "appid": WEATHER_API_KEY, "units": "metric"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()


async def get_forecast(lat: float, lon: float, hours: int = 48) -> list[dict]:
    """Fetch hourly forecast for prediction window."""
    if not WEATHER_API_KEY:
        return [_mock_weather() for _ in range(8)]
    url = f"{WEATHER_BASE_URL}/forecast"
    params = {"lat": lat, "lon": lon, "appid": WEATHER_API_KEY, "units": "metric", "cnt": max(1, hours // 3)}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("list", [])


def _mock_weather() -> dict:
    """Return plausible mock weather for development."""
    return {
        "main": {"temp": 28, "humidity": 75, "temp_min": 26, "temp_max": 30},
        "wind": {"speed": 3.5, "gust": 8.0},
        "rain": {"1h": 2.5} if datetime.now().hour % 3 == 0 else {},
        "weather": [{"main": "Rain", "description": "light rain", "id": 500}],
    }
