"""Zone-level risk prediction (Tier A).

Phase 1: Rules-based using weather thresholds + outage density.
Phase 2: Statistical model (XGBoost).
Phase 3: Graph neural network with cascade prediction.
"""

import math
from datetime import datetime, UTC
from app.services.weather import get_current_weather, get_forecast
from app.models.schemas import ZoneRiskResponse
from app.config import logger

RISK_THRESHOLDS = {"LOW": 0.0, "MEDIUM": 0.3, "HIGH": 0.6, "CRITICAL": 0.85}

WEATHER_FACTORS = {
    "Thunderstorm": 0.35,
    "Rain": 0.15,
    "Drizzle": 0.05,
    "Snow": 0.10,
}

WIND_GUST_THRESHOLD = 15.0  # m/s
RAIN_THRESHOLD_1H = 10.0  # mm


def _compute_zone_risk_rules(
    weather: dict,
    forecast: list[dict],
    outage_count: int,
) -> tuple[float, list[str]]:
    """Phase 1: Rule-based zone risk scoring."""
    factors = []
    score = 0.0

    main_weather = weather.get("weather", [{}])[0].get("main", "")
    base_factor = WEATHER_FACTORS.get(main_weather, 0.0)
    if base_factor > 0:
        score += base_factor
        factors.append(f"Weather: {main_weather}")

    rain_1h = weather.get("rain", {}).get("1h", 0)
    if rain_1h > RAIN_THRESHOLD_1H:
        score += 0.15
        factors.append(f"Heavy rain: {rain_1h}mm/h")

    wind_gust = weather.get("wind", {}).get("gust", 0)
    if wind_gust > WIND_GUST_THRESHOLD:
        score += 0.20
        factors.append(f"Strong wind gust: {wind_gust}m/s")

    max_forecast_rain = max(
        (f.get("rain", {}).get("3h", 0) for f in forecast),
        default=0,
    )
    if max_forecast_rain > 20:
        score += 0.10
        factors.append(f"Forecast: {max_forecast_rain}mm/3h expected")

    outage_density_risk = min(outage_count * 0.05, 0.25)
    if outage_density_risk > 0:
        score += outage_density_risk
        factors.append(f"Outage reports: {outage_count} in 6h")

    score = min(score, 1.0)
    return round(score, 4), factors


async def predict_zone_risk(
    zone_id: str,
    lat: float,
    lon: float,
    outage_count: int,
) -> ZoneRiskResponse:
    """Predict outage risk for a zone."""
    weather = await get_current_weather(lat, lon)
    forecast = await get_forecast(lat, lon, hours=6)
    score, factors = _compute_zone_risk_rules(weather, forecast, outage_count)

    risk_level = "LOW"
    for level, threshold in sorted(RISK_THRESHOLDS.items(), key=lambda x: -x[1]):
        if score >= threshold:
            risk_level = level
            break

    logger.info(
        "Zone risk | zone=%s score=%.3f level=%s factors=%s",
        zone_id, score, risk_level, factors,
    )

    return ZoneRiskResponse(
        zone_id=zone_id,
        risk_score=score,
        risk_level=risk_level,
        window_hours=6,
        predicted_at=datetime.now(UTC),
        contributing_factors=factors,
    )
