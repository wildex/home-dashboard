import pytest
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from home_dashboard.main import create_app
from home_dashboard.db import init_db

@pytest.mark.asyncio
async def test_interval_update_creates_new_future_task():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/appliances/", json={"name": "IntervalTester", "cleaning_interval_days": 5})
        appliance_id = resp.json()["id"]
        tasks_before = await client.get(f"/api/appliances/{appliance_id}/tasks")
        assert len(tasks_before.json()) >= 1
        upd = await client.patch(f"/api/appliances/{appliance_id}/interval", json={"cleaning_interval_days": 10})
        assert upd.status_code == 200
        tasks_after = await client.get(f"/api/appliances/{appliance_id}/tasks")
        expected_date = date.today() + timedelta(days=10)
        assert any(t["due_date"] == str(expected_date) and not t["completed"] for t in tasks_after.json())

@pytest.mark.asyncio
async def test_unschedule_removes_future_tasks():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/appliances/", json={"name": "UnscheduleTester", "cleaning_interval_days": 3})
        appliance_id = resp.json()["id"]
        upd = await client.patch(f"/api/appliances/{appliance_id}/interval", json={"cleaning_interval_days": None})
        assert upd.status_code == 200
        tasks_after = await client.get(f"/api/appliances/{appliance_id}/tasks")
        assert not any(not t["completed"] for t in tasks_after.json())

@pytest.mark.asyncio
async def test_completed_task_timestamp_utc():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/appliances/", json={"name": "UTC Tester", "cleaning_interval_days": 2})
        appliance_id = resp.json()["id"]
        tasks = await client.get(f"/api/appliances/{appliance_id}/tasks")
        task_id = tasks.json()[0]["id"]
        comp = await client.patch(f"/api/tasks/{task_id}", json={"completed": True})
        assert comp.status_code == 200
        task_after = comp.json()
        assert task_after["completed_at"].endswith("+00:00") or task_after["completed_at"].endswith("Z")
