from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ZoneRiskRequest, ZoneRiskResponse,
    TransformerRiskRequest, TransformerRiskResponse,
    DispatchRecommendation,
)
from app.services.zone_risk import predict_zone_risk
from app.services.transformer_risk import predict_transformer_risk, recommend_dispatch
from app.config import ZONE_RISK_ENABLED, TRANSFORMER_RISK_ENABLED, HITL_ENABLED

router = APIRouter(prefix="/v1", tags=["prediction"])


@router.post("/predict/zone", response_model=ZoneRiskResponse)
async def predict_zone(req: ZoneRiskRequest):
    if not ZONE_RISK_ENABLED:
        raise HTTPException(status_code=503, detail="Zone risk prediction is disabled")
    return await predict_zone_risk(
        zone_id=req.zone_id,
        lat=req.latitude,
        lon=req.longitude,
        outage_count=req.recent_outage_count,
    )


@router.post("/predict/transformer", response_model=TransformerRiskResponse)
async def predict_transformer(req: TransformerRiskRequest):
    if not TRANSFORMER_RISK_ENABLED:
        raise HTTPException(status_code=503, detail="Transformer risk prediction is disabled")
    return await predict_transformer_risk(
        transformer_id=req.transformer_id,
        zone_id=req.zone_id,
        age_years=req.asset_age_years,
        load_pct=req.load_percentage,
        inspection_score=req.last_inspection_score,
        outage_count=req.recent_outage_count,
    )


@router.post("/recommend/dispatch", response_model=DispatchRecommendation | None)
async def recommend(req: TransformerRiskRequest):
    if not HITL_ENABLED:
        raise HTTPException(status_code=503, detail="HITL dispatch is disabled")
    risk = await predict_transformer_risk(
        transformer_id=req.transformer_id,
        zone_id=req.zone_id,
        age_years=req.asset_age_years,
        load_pct=req.load_percentage,
        inspection_score=req.last_inspection_score,
        outage_count=req.recent_outage_count,
    )
    return await recommend_dispatch(risk)
