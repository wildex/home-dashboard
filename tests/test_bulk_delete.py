import pytest
from httpx import AsyncClient, ASGITransport
from home_dashboard.main import create_app
from home_dashboard.db import init_db

@pytest.mark.asyncio
async def test_bulk_delete_selected_appliances():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # create three appliances
        for name in ["ToDelete1", "ToDelete2", "KeepMe"]:
            await client.post("/api/appliances/", json={"name": name, "cleaning_interval_days": 5})
        # fetch list via API
        api_list = await client.get("/api/appliances/")
        ids_map = {a["name"]: a["id"] for a in api_list.json()}
        delete_ids = [ids_map["ToDelete1"], ids_map["ToDelete2"]]
        # bulk delete
        resp = await client.post("/api/appliances/bulk-delete", json={"ids": delete_ids})
        assert resp.status_code == 200
        # verify remaining
        remaining = await client.get("/api/appliances/")
        names = {a["name"] for a in remaining.json()}
        assert "KeepMe" in names
        assert "ToDelete1" not in names
        assert "ToDelete2" not in names

@pytest.mark.asyncio
async def test_bulk_delete_none_selected_returns_error():
    app = create_app()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/appliances/", json={"name": "X", "cleaning_interval_days": 3})
        resp = await client.post("/api/appliances/bulk-delete", json={"ids": []})
        assert resp.status_code == 422  # validation fails (min_length=1)
