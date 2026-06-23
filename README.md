# Streemline Predictive OMS

**Outcome:** Predict power outages at zone and transformer level before they happen.

Built for the Electricity Company of Ghana (ECG). WhatsApp-first customer interface. Human-in-the-loop dispatch. Continuous learning.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  WhatsApp    │────▶│  Go Bridge   │────▶│  Prediction  │
│  (whatsmeow) │     │  Connector   │     │  Engine      │
└──────────────┘     └──────────────┘     │  (FastAPI)    │
                                          │  :8001        │
┌──────────────┐     ┌──────────────┐     └──────┬───────┘
│  ECG Ops     │◀────│  Web Admin   │            │
│  WhatsApp    │     │  Dashboard   │     ┌──────▼───────┐
└──────────────┘     └──────────────┘     │  Weather API │
                                          │  (OpenWeather)│
                                          └──────────────┘
```

## Quick Start

```bash
# All services
make dev

# Prediction engine only
cd prediction-engine
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Dashboard only
make dev-dashboard
```

## Prediction Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health + feature flags |
| POST | `/v1/predict/zone` | Zone-level outage risk (6h window) |
| POST | `/v1/predict/transformer` | Transformer failure probability (48h) |
| POST | `/v1/recommend/dispatch` | HITL dispatch recommendation |

## Deployment

```bash
docker compose up --build -d
```

## ML Roadmap

| Phase | Timeline | Model | Inputs |
|-------|----------|-------|--------|
| 1 | Week 1 | Rules | Weather + outage density |
| 2 | Month 3 | XGBoost | + historical outages, load data |
| 3 | Month 6 | GNN | + grid topology, cascade effects |
