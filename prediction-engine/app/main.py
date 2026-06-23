from fastapi import FastAPI
from app.api import predict, health
from app.services import zone_risk, transformer_risk, weather

app = FastAPI(
    title="Streemline Predictive OMS",
    description="Two-tier outage prediction for ECG (Zone Risk + Transformer Risk)",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(predict.router)
