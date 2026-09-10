"""
Tests for FastAPI endpoints: /health, /status, /api/analyze.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.api.server import api_app
from app.database.database import db


@pytest.mark.asyncio
async def test_health_endpoint():
    await db.init_db()
    transport = ASGITransport(app=api_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "pocket-option-ai-analyzer"


@pytest.mark.asyncio
async def test_status_endpoint():
    await db.init_db()
    transport = ASGITransport(app=api_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "operational"
        assert "registered_users" in data


@pytest.mark.asyncio
async def test_api_analyze_endpoint():
    await db.init_db()
    transport = ASGITransport(app=api_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/analyze",
            json={"asset": "EUR/USD", "timeframe": "M1", "expiration": "1m"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset"] == "EUR/USD"
        assert data["decision"] in ["CALL", "PUT", "NO TRADE"]
        assert 0.0 <= data["confidence"] <= 100.0
        assert "market_structure" in data
        assert "execution_time_ms" in data
