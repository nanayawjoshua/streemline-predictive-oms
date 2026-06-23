from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import ZONE_RISK_ENABLED, TRANSFORMER_RISK_ENABLED

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version="0.1.0",
        tier_a_active=ZONE_RISK_ENABLED,
        tier_b_active=TRANSFORMER_RISK_ENABLED,
    )


@router.get("/", response_model=HealthResponse)
async def root():
    return await health()
