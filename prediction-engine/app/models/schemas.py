from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ZoneRiskRequest(BaseModel):
    zone_id: str = Field(..., description="Electoral area / zone identifier")
    latitude: float
    longitude: float
    recent_outage_count: int = Field(0, ge=0, description="Outage reports in last 6h")

class ZoneRiskResponse(BaseModel):
    zone_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: str  # LOW / MEDIUM / HIGH / CRITICAL
    window_hours: int = 6
    predicted_at: datetime
    contributing_factors: list[str]

class TransformerRiskRequest(BaseModel):
    transformer_id: str
    zone_id: str
    asset_age_years: float
    load_percentage: float = Field(..., ge=0, le=100)
    last_inspection_score: Optional[float] = Field(None, ge=0, le=100)
    recent_outage_count: int = 0

class TransformerRiskResponse(BaseModel):
    transformer_id: str
    failure_probability: float = Field(..., ge=0, le=1)
    risk_level: str
    window_hours: int = 48
    predicted_at: datetime
    days_to_maintenance: Optional[int]

class DispatchRecommendation(BaseModel):
    transformer_id: str
    zone_id: str
    urgency: str  # IMMEDIATE / NEXT_SHIFT / SCHEDULED
    reason: str
    suggested_team_size: int = 2

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    tier_a_active: bool = True
    tier_b_active: bool = False
