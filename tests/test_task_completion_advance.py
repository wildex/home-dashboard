import pytest
from httpx import AsyncClient, ASGITransport
from home_dashboard.main import create_app
from home_dashboard.db import init_db

@pytest.mark.asyncio
async def test_task_completion_creates_later_due_date():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create appliance with 5 day interval
        r = await client.post('/api/appliances/', json={'name': 'AdvanceTester', 'cleaning_interval_days': 5})
        assert r.status_code == 200 or r.status_code == 201
        appliance_id = r.json()['id']
        # Fetch its tasks
        tasks_resp = await client.get(f'/api/appliances/{appliance_id}/tasks')
        assert tasks_resp.status_code == 200
        tasks = tasks_resp.json()
        assert len(tasks) >= 1
        first_task = tasks[0]
        first_due = first_task['due_date']
        # Complete the first task
        comp = await client.patch(f"/api/tasks/{first_task['id']}", json={'completed': True})
        assert comp.status_code == 200
        # Fetch tasks again
        tasks_resp2 = await client.get(f'/api/appliances/{appliance_id}/tasks')
        assert tasks_resp2.status_code == 200
        tasks2 = tasks_resp2.json()
        # There should be at least one incomplete task with later due date
        later_tasks = [t for t in tasks2 if not t['completed']]
        assert later_tasks, 'No new incomplete task scheduled'
        # All new incomplete tasks must have due date strictly greater than previous due
        assert all(t['due_date'] > first_due for t in later_tasks), f"Found task with non-advanced due date: {later_tasks}"
