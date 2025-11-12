import pytest
from httpx import AsyncClient, ASGITransport
from home_dashboard.main import create_app
from home_dashboard.db import init_db

@pytest.mark.asyncio
async def test_create_appliance_generates_task():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/appliances/", json={"name": "Dishwasher", "cleaning_interval_days": 30})
        assert resp.status_code == 201
        appliance = resp.json()
        assert appliance["name"] == "Dishwasher"
        # list tasks
        tasks_resp = await client.get(f"/api/appliances/{appliance['id']}/tasks")
        tasks = tasks_resp.json()
        assert len(tasks) == 1
        assert tasks[0]["completed"] is False

@pytest.mark.asyncio
async def test_complete_task_creates_next():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/appliances/", json={"name": "Cat Fountain", "cleaning_interval_days": 7})
        appliance = resp.json()
        tasks_resp = await client.get(f"/api/appliances/{appliance['id']}/tasks")
        task = tasks_resp.json()[0]
        # complete
        complete_resp = await client.patch(f"/api/tasks/{task['id']}", json={"completed": True})
        assert complete_resp.status_code == 200
        # list again -> should have previous + new future task
        tasks_resp2 = await client.get(f"/api/appliances/{appliance['id']}/tasks")
        tasks2 = tasks_resp2.json()
        assert len(tasks2) == 2
        assert any(t["completed"] for t in tasks2)
        assert any(not t["completed"] for t in tasks2)
