import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.db.database import init_db
from app.simulation.engine import sim_engine
from app.world.town_map import town_map
from app.core.events import event_bus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("genesis")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, data: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()

# Register WebSocket broadcaster with sim_engine tick listeners
async def on_tick_broadcast(state: Dict[str, Any]):
    if ws_manager.active_connections:
        await ws_manager.broadcast({
            "type": "TICK_UPDATE",
            "data": state
        })

sim_engine.tick_listeners.append(on_tick_broadcast)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Project Genesis backend...")
    await init_db()
    await sim_engine.initialize()
    # Try restoring from db or start fresh
    restored = await sim_engine.restore_from_db()
    if restored:
        logger.info("Restored simulation state from SQLite checkpoint.")
    else:
        logger.info("Starting fresh simulation world.")
        
    sim_engine.start_background_loop()
    yield
    # Shutdown
    logger.info("Shutting down Project Genesis...")
    sim_engine.stop_background_loop()
    await sim_engine.save_checkpoint_to_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class SpeedRequest(BaseModel):
    speed: float

class InjectEventRequest(BaseModel):
    event_type: str = "community"
    description: str
    location_id: str
    significance: float = 7.0

# REST Endpoints
@app.get("/api/world/state")
async def get_world_state():
    return sim_engine.get_full_state()

@app.get("/api/world/map")
async def get_town_map():
    return town_map.get_map_metadata()

@app.get("/api/npcs")
async def get_npcs():
    return [agent.to_dict() for agent in sim_engine.npcs.values()]

@app.get("/api/npcs/{npc_id}")
async def get_npc_profile(npc_id: str):
    agent = sim_engine.npcs.get(npc_id)
    if not agent:
        raise HTTPException(status_code=404, detail="NPC not found")
    data = agent.to_dict()
    data["full_schedule"] = agent.planner.to_dict()
    return data

@app.get("/api/npcs/{npc_id}/memories")
async def get_npc_memories(
    npc_id: str,
    memory_type: Optional[str] = None,
    query: Optional[str] = None
):
    agent = sim_engine.npcs.get(npc_id)
    if not agent:
        raise HTTPException(status_code=404, detail="NPC not found")

    if query:
        # Semantic retrieval query
        mems = agent.memory.retrieve(
            query=query,
            current_sim_minute=sim_engine.clock.total_sim_minutes,
            top_k=10
        )
        return [m.to_dict() for m in mems]
        
    mems = agent.memory.memories
    if memory_type:
        mems = [m for m in mems if m.memory_type == memory_type]
        
    return [m.to_dict() for m in mems]

@app.get("/api/npcs/{npc_id}/relationships")
async def get_npc_relationships(npc_id: str):
    agent = sim_engine.npcs.get(npc_id)
    if not agent:
        raise HTTPException(status_code=404, detail="NPC not found")
    return agent.relationships.get_all()

@app.get("/api/social/graph")
async def get_social_graph():
    """Graph structure formatted for React Flow visualization."""
    nodes = []
    edges = []
    
    for agent in sim_engine.npcs.values():
        nodes.append({
            "id": agent.id,
            "name": agent.name,
            "occupation": agent.identity.occupation,
            "color": agent.identity.avatar_color,
            "location": agent.current_location,
            "emotion": agent.emotions.current_emotion.value
        })
        
        for rel in agent.relationships.relationships.values():
            if rel.familiarity > 15.0:
                edges.append({
                    "id": f"{rel.source_npc_id}_{rel.target_npc_id}",
                    "source": rel.source_npc_id,
                    "target": rel.target_npc_id,
                    "familiarity": rel.familiarity,
                    "trust": rel.trust,
                    "affinity": rel.affinity,
                    "conflict": rel.conflict,
                    "type": rel.relationship_type
                })
                
    return {"nodes": nodes, "edges": edges}

@app.get("/api/events")
async def get_events(limit: int = Query(50, ge=1, le=200)):
    return event_bus.get_recent_history(limit=limit)

# Simulation Controls
@app.post("/api/simulation/pause")
async def pause_simulation():
    sim_engine.clock.pause()
    return {"status": "paused", "state": sim_engine.clock.get_state()}

@app.post("/api/simulation/resume")
async def resume_simulation():
    sim_engine.clock.resume()
    return {"status": "running", "state": sim_engine.clock.get_state()}

@app.post("/api/simulation/speed")
async def set_simulation_speed(req: SpeedRequest):
    sim_engine.clock.set_speed(req.speed)
    return {"status": "speed_updated", "speed": sim_engine.clock.speed_multiplier}

@app.post("/api/simulation/step")
async def step_simulation():
    state = await sim_engine.tick()
    return {"status": "stepped", "state": state}

@app.post("/api/simulation/reset")
async def reset_simulation():
    sim_engine.stop_background_loop()
    sim_engine.clock.reset()
    sim_engine.is_initialized = False
    await sim_engine.initialize()
    sim_engine.start_background_loop()
    return {"status": "reset"}

@app.post("/api/simulation/checkpoint/save")
async def save_checkpoint():
    await sim_engine.save_checkpoint_to_db()
    return {"status": "checkpoint_saved"}

@app.post("/api/simulation/checkpoint/restore")
async def restore_checkpoint():
    success = await sim_engine.restore_from_db()
    return {"status": "restored" if success else "failed"}

@app.post("/api/simulation/inject_event")
async def inject_event(req: InjectEventRequest):
    event = sim_engine.inject_world_event(
        event_type=req.event_type,
        description=req.description,
        location_id=req.location_id,
        significance=req.significance
    )
    return {"status": "event_injected", "event": event.dict()}

# WebSocket Connection
@app.websocket("/ws/simulation")
async def simulation_websocket(websocket: WebSocket):
    await ws_manager.connect(websocket)
    # Send initial state
    await websocket.send_json({
        "type": "INITIAL_STATE",
        "data": sim_engine.get_full_state()
    })
    try:
        while True:
            # Listen for client control commands over WebSocket
            msg = await websocket.receive_json()
            cmd = msg.get("command")
            if cmd == "PAUSE":
                sim_engine.clock.pause()
            elif cmd == "RESUME":
                sim_engine.clock.resume()
            elif cmd == "STEP":
                await sim_engine.tick()
            elif cmd == "SET_SPEED":
                sim_engine.clock.set_speed(float(msg.get("speed", 1.0)))
            elif cmd == "INJECT_EVENT":
                sim_engine.inject_world_event(
                    event_type=msg.get("event_type", "community"),
                    description=msg.get("description", "A strange rumor spreads"),
                    location_id=msg.get("location_id", "town_square"),
                    significance=float(msg.get("significance", 7.0))
                )
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
