import pytest
from httpx import AsyncClient, ASGITransport
from home_dashboard.main import create_app
from home_dashboard.db import init_db

@pytest.mark.asyncio
async def test_temperature_rooms_and_clear():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Add readings for two rooms
        await client.post('/api/temperature/', json={'value_c': 20.1, 'room': 'living'})
        await client.post('/api/temperature/', json={'value_c': 21.4, 'room': 'living'})
        await client.post('/api/temperature/', json={'value_c': 18.7, 'room': 'office'})
        # Dashboard should group
        resp = await client.get('/api/dashboard')
        assert resp.status_code == 200
        data = resp.json()
        assert 'recent_temps_by_room' in data
        assert set(data['recent_temps_by_room'].keys()) == {'living', 'office'}
        assert len(data['recent_temps_by_room']['living']) == 2
        assert len(data['recent_temps_by_room']['office']) == 1
        # Clear one room
        clr = await client.delete('/api/temperature/?room=living')
        assert clr.status_code == 200
        assert clr.json()['deleted'] >= 2
        resp2 = await client.get('/api/dashboard')
        data2 = resp2.json()
        assert 'living' not in data2['recent_temps_by_room'] or len(data2['recent_temps_by_room']['living']) == 0
        assert 'office' in data2['recent_temps_by_room']
        # Clear all remaining
        clr_all = await client.delete('/api/temperature/')
        assert clr_all.status_code == 200
        resp3 = await client.get('/api/dashboard')
        data3 = resp3.json()
        # office removed
        assert 'office' not in data3['recent_temps_by_room']

