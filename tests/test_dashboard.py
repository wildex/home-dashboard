import pytest
from httpx import AsyncClient, ASGITransport
from home_dashboard.main import create_app
from home_dashboard.db import init_db

@pytest.mark.asyncio
async def test_dashboard_json():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # seed data via API
        await client.post("/api/appliances/", json={"name": "Dishwasher", "cleaning_interval_days": 30})
        await client.post("/api/temperature/", json={"value_c": 21.5})
        resp = await client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "due_tasks" in data
        assert "recent_temps" in data
