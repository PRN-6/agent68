import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.simulation.engine import sim_engine
from app.db.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_sim():
    await init_db()
    await sim_engine.initialize()

@pytest.mark.asyncio
async def test_api_world_state_and_map():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. World State
        res_state = await client.get("/api/world/state")
        assert res_state.status_code == 200
        data_state = res_state.json()
        assert "clock" in data_state
        assert "weather" in data_state
        assert "npcs" in data_state
        assert len(data_state["npcs"]) == 25

        # 2. Town Map
        res_map = await client.get("/api/world/map")
        assert res_map.status_code == 200
        data_map = res_map.json()
        assert "locations" in data_map
        assert "roads" in data_map
        assert "districts" in data_map

@pytest.mark.asyncio
async def test_api_npcs_and_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. All NPCs
        res_npcs = await client.get("/api/npcs")
        assert res_npcs.status_code == 200
        npcs = res_npcs.json()
        assert len(npcs) == 25

        first_npc = npcs[0]
        # 2. Individual Profile
        res_profile = await client.get(f"/api/npcs/{first_npc['id']}")
        assert res_profile.status_code == 200
        profile = res_profile.json()
        assert profile["name"] == first_npc["name"]
        assert "full_schedule" in profile

        # 3. Memories
        res_mems = await client.get(f"/api/npcs/{first_npc['id']}/memories")
        assert res_mems.status_code == 200
        mems = res_mems.json()
        assert len(mems) >= 1

        # 4. Social Graph
        res_graph = await client.get("/api/social/graph")
        assert res_graph.status_code == 200
        graph = res_graph.json()
        assert "nodes" in graph
        assert len(graph["nodes"]) == 25

@pytest.mark.asyncio
async def test_api_controls_and_god_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Step simulation
        res_step = await client.post("/api/simulation/step")
        assert res_step.status_code == 200
        assert res_step.json()["status"] == "stepped"

        # 2. Speed update
        res_speed = await client.post("/api/simulation/speed", json={"speed": 5.0})
        assert res_speed.status_code == 200
        assert res_speed.json()["speed"] == 5.0

        # 3. Inject event
        res_inj = await client.post(
            "/api/simulation/inject_event",
            json={
                "event_type": "community",
                "description": "Grand festival celebration announced!",
                "location_id": "town_square",
                "significance": 8.0
            }
        )
        assert res_inj.status_code == 200
        assert res_inj.json()["status"] == "event_injected"
