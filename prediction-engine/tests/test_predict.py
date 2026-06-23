import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["tier_a_active"] is True


@pytest.mark.asyncio
async def test_zone_risk_prediction(client):
    resp = await client.post(
        "/v1/predict/zone",
        json={
            "zone_id": "adenta-001",
            "latitude": 5.66,
            "longitude": -0.16,
            "recent_outage_count": 3,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["zone_id"] == "adenta-001"
    assert 0 <= data["risk_score"] <= 1
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert len(data["contributing_factors"]) > 0
