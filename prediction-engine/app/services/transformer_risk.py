"""Transformer-level risk prediction (Tier B).

Phase 1: Statistical baseline (age + load + inspection score).
Phase 2: XGBoost (requires ZEUS API data for training).
Phase 3: Graph neural network with cascade effects.
"""

import math
from datetime import datetime, UTC
from app.models.schemas import TransformerRiskResponse, DispatchRecommendation
from app.config import logger

RISK_THRESHOLDS = {"LOW": 0.0, "MEDIUM": 0.25, "HIGH": 0.5, "CRITICAL": 0.75}
MAX_AGE_YEARS = 40  # typical transformer lifespan


def _compute_transformer_risk(
    age_years: float,
    load_pct: float,
    inspection_score: float | None,
    outage_count: int,
) -> float:
    """Phase 1: Statistical transformer failure probability."""
    age_factor = min(age_years / MAX_AGE_YEARS, 1.0) * 0.35

    load_factor = 0.0
    if load_pct > 90:
        load_factor = 0.25
    elif load_pct > 75:
        load_factor = 0.10
    elif load_pct > 60:
        load_factor = 0.05

    inspection_factor = 0.0
    if inspection_score is not None:
        inspection_factor = max(0, (100 - inspection_score) / 100) * 0.25

    outage_factor = min(outage_count * 0.03, 0.15)

    score = age_factor + load_factor + inspection_factor + outage_factor
    return round(min(score, 1.0), 4)


async def predict_transformer_risk(
    transformer_id: str,
    zone_id: str,
    age_years: float,
    load_pct: float,
    inspection_score: float | None,
    outage_count: int,
) -> TransformerRiskResponse:
    """Predict failure risk for a single transformer."""
    score = _compute_transformer_risk(age_years, load_pct, inspection_score, outage_count)

    risk_level = "LOW"
    for level, threshold in sorted(RISK_THRESHOLDS.items(), key=lambda x: -x[1]):
        if score >= threshold:
            risk_level = level
            break

    days_to_maintenance = None
    if risk_level in ("HIGH", "CRITICAL"):
        days_to_maintenance = max(1, int(30 * (1 - score)))

    logger.info(
        "Transformer risk | xformer=%s zone=%s score=%.3f level=%s",
        transformer_id, zone_id, score, risk_level,
    )

    return TransformerRiskResponse(
        transformer_id=transformer_id,
        failure_probability=score,
        risk_level=risk_level,
        window_hours=48,
        predicted_at=datetime.now(UTC),
        days_to_maintenance=days_to_maintenance,
    )


async def recommend_dispatch(
    risk: TransformerRiskResponse,
) -> DispatchRecommendation | None:
    """Generate dispatch recommendation for HITL approval."""
    if risk.risk_level == "CRITICAL":
        return DispatchRecommendation(
            transformer_id=risk.transformer_id,
            zone_id="",
            urgency="IMMEDIATE",
            reason=f"Critical failure risk ({risk.failure_probability:.0%}). "
                   f"Recommended maintenance within {risk.days_to_maintenance} days.",
            suggested_team_size=3,
        )
    if risk.risk_level == "HIGH":
        return DispatchRecommendation(
            transformer_id=risk.transformer_id,
            zone_id="",
            urgency="NEXT_SHIFT",
            reason=f"High failure risk ({risk.failure_probability:.0%}). "
                   f"Schedule inspection within {risk.days_to_maintenance} days.",
            suggested_team_size=2,
        )
    return None
