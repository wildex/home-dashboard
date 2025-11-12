import pytest
from httpx import AsyncClient, ASGITransport
from home_dashboard.main import create_app
from home_dashboard.db import init_db

@pytest.mark.asyncio
async def test_api_flow_interval_and_completion():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # create appliance
        r = await client.post("/api/appliances/", json={"name": "FlowTester", "cleaning_interval_days": 5})
        appliance = r.json()
        # update interval
        upd = await client.patch(f"/api/appliances/{appliance['id']}/interval", json={"cleaning_interval_days": 10})
        assert upd.status_code == 200
        assert upd.json()["cleaning_interval_days"] == 10
        # fetch tasks
        tasks_resp = await client.get(f"/api/appliances/{appliance['id']}/tasks")
        task = tasks_resp.json()[0]
        # complete task
        comp = await client.patch(f"/api/tasks/{task['id']}", json={"completed": True})
        assert comp.status_code == 200
        assert comp.json()["completed"] is True
