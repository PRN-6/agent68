import asyncio
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import select

from app.core.clock import SimulationClock
from app.core.weather import WeatherSystem
from app.core.events import event_bus
from app.agents.population import initialize_population
from app.agents.npc import NPCAgent
from app.agents.conversation import ConversationSession
from app.agents.party import party_manager
from app.world.locations import TOWN_LOCATIONS, get_all_locations
from app.db.database import AsyncSessionLocal
from app.db.models import NPCModel, MemoryModel, RelationshipModel, SimulationStateModel
from app.config import settings

logger = logging.getLogger(__name__)

class SimulationEngine:
    def __init__(self):
        self.clock = SimulationClock(start_hour=7, start_minute=0, start_day=1)
        self.weather = WeatherSystem()
        self.npcs: Dict[str, NPCAgent] = {}
        self.active_conversations: List[ConversationSession] = []
        self.is_initialized: bool = False
        self.sim_task: Optional[asyncio.Task] = None
        self.tick_listeners: List[Any] = []
        self.stats = {
            "total_decisions": 0,
            "total_conversations": 0,
            "total_reflections": 0,
            "sim_tick_duration_ms": 0.0
        }

    async def initialize(self):
        """Boot world simulation and populate 25 agents."""
        if self.is_initialized:
            return

        logger.info("Initializing Project Genesis simulation engine...")
        agents = initialize_population()
        self.npcs = {agent.id: agent for agent in agents}

        # Generate initial daily plans for all 25 agents
        for agent in self.npcs.values():
            await agent.planner.generate_schedule_for_day(
                npc_data=agent.get_profile_dict(),
                sim_day=self.clock.sim_day,
                date_str=f"Day {self.clock.sim_day}",
                current_needs=agent.needs.to_dict()
            )

        self.is_initialized = True
        logger.info(f"Initialized {len(self.npcs)} autonomous agents successfully.")

    async def tick(self) -> Dict[str, Any]:
        """Perform a single deterministic simulation step."""
        t_start = datetime.utcnow()
        clock_state = self.clock.tick()
        sim_minute = self.clock.total_sim_minutes
        sim_hour = self.clock.sim_hour
        sim_day = self.clock.sim_day

        # 1. Hourly Weather Update
        weather_state = self.weather.get_state()
        if clock_state.get("hour_rolled"):
            weather_state = self.weather.tick_hourly()

        # 2. Daily Planning for new day
        if clock_state.get("day_rolled"):
            for agent in self.npcs.values():
                await agent.planner.generate_schedule_for_day(
                    npc_data=agent.get_profile_dict(),
                    sim_day=sim_day,
                    date_str=f"Day {sim_day}",
                    current_needs=agent.needs.to_dict()
                )

        known_locations = list(TOWN_LOCATIONS.keys())

        # Group NPCs by location for proximity detection
        npcs_by_location: Dict[str, List[NPCAgent]] = {}
        for agent in self.npcs.values():
            loc = agent.current_location
            if loc not in npcs_by_location:
                npcs_by_location[loc] = []
            npcs_by_location[loc].append(agent)

        # 3. Update Each Agent
        for agent in self.npcs.values():
            co_located = [
                n.get_profile_dict()
                for n in npcs_by_location.get(agent.current_location, [])
                if n.id != agent.id
            ]
            await agent.update_tick(
                sim_minute=sim_minute,
                sim_hour=sim_hour,
                sim_day=sim_day,
                weather=weather_state,
                nearby_npcs=co_located,
                known_locations=known_locations
            )

        # 4. Emergent Conversation Detection
        # Check locations with 2+ free agents and trigger spontaneous dialogue
        if self.clock.tick_count % 3 == 0:  # Check periodically
            for loc_id, agents_at_loc in npcs_by_location.items():
                if len(agents_at_loc) >= 2 and not loc_id.startswith("home_"):
                    available = [
                        a for a in agents_at_loc
                        if not a.path_queue and "sleep" not in a.current_activity.lower() and "talk" not in a.current_activity.lower()
                    ]
                    if len(available) >= 2 and random.random() < 0.25:
                        p1, p2 = random.sample(available, 2)
                        # Check they haven't conversed in the last 20 minutes
                        rel = p1.relationships.get_or_create(p2.id)
                        if sim_minute - rel.last_interaction_minute >= 20:
                            topic_pool = [
                                "the upcoming autumn community festival",
                                f"the {weather_state['type']} weather today",
                                "recent commerce opportunities at the marketplace",
                                "town history and local news"
                            ]
                            chosen_topic = random.choice(topic_pool)
                            p1.current_activity = f"Talking with {p2.name.split()[0]}"
                            p2.current_activity = f"Talking with {p1.name.split()[0]}"
                            p1.action_minutes_remaining = 8
                            p2.action_minutes_remaining = 8
                            session = ConversationSession(p1, p2, loc_id, sim_minute, topic=chosen_topic)
                            self.active_conversations.append(session)
                            await session.execute_dialogue(max_turns=3)
                            self.stats["total_conversations"] += 1
                            if len(self.active_conversations) > 20:
                                self.active_conversations.pop(0)

        # 5. MMORPG Adventuring Parties & Dungeon Expeditions Tick
        await party_manager.update_tick(self.npcs, sim_minute)

        t_end = datetime.utcnow()
        self.stats["sim_tick_duration_ms"] = round((t_end - t_start).total_seconds() * 1000.0, 2)

        state_snapshot = self.get_full_state()
        
        # Notify subscribers (WebSocket clients)
        for listener in self.tick_listeners:
            try:
                await listener(state_snapshot)
            except Exception as e:
                logger.error(f"Error notifying tick listener: {e}")

        return state_snapshot

    def start_background_loop(self):
        if self.sim_task is None or self.sim_task.done():
            self.clock.resume()
            self.sim_task = asyncio.create_task(self._simulation_loop())

    def stop_background_loop(self):
        self.clock.pause()
        if self.sim_task and not self.sim_task.done():
            self.sim_task.cancel()

    async def _simulation_loop(self):
        """Continuous simulation runner respecting speed multipliers."""
        while True:
            try:
                if self.clock.is_running:
                    await self.tick()
                    
                # Delay based on tick rate and speed multiplier
                base_delay = settings.DEFAULT_TICK_RATE_MS / 1000.0
                actual_delay = max(0.02, base_delay / self.clock.speed_multiplier)
                await asyncio.sleep(actual_delay)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}", exc_info=True)
                await asyncio.sleep(0.5)

    def inject_world_event(
        self,
        event_type: str,
        description: str,
        location_id: str,
        significance: float = 7.0
    ):
        """God-mode intervention: publish unexpected event and prompt nearby NPCs to replan!"""
        event = event_bus.publish_event(
            event_type=event_type,
            description=description,
            location_id=location_id,
            sim_timestamp=self.clock.total_sim_minutes,
            significance=significance,
            present_npc_ids=[a.id for a in self.npcs.values() if a.current_location == location_id]
        )

        # Notify NPCs at or near this location
        for agent in self.npcs.values():
            if agent.current_location == location_id or random.random() < 0.3:
                agent.add_memory(
                    content=f"Witnessed / heard event: {description}",
                    sim_minute=self.clock.total_sim_minutes,
                    importance=significance
                )
                # Trigger dynamic replanning
                asyncio.create_task(agent.planner.handle_unexpected_event(
                    npc_data=agent.get_profile_dict(),
                    event_description=description,
                    current_needs=agent.needs.to_dict()
                ))

        return event

    async def save_checkpoint_to_db(self):
        """Persist full simulation state, agent identities, memories, and relationships to SQLite."""
        async with AsyncSessionLocal() as session:
            try:
                # 1. Save Clock & Sim State
                state_record = await session.get(SimulationStateModel, 1)
                if not state_record:
                    state_record = SimulationStateModel(id=1)
                    session.add(state_record)

                state_record.tick = self.clock.tick_count
                state_record.sim_minute = self.clock.sim_minute
                state_record.sim_hour = self.clock.sim_hour
                state_record.sim_day = self.clock.sim_day
                state_record.weather = self.weather.current_weather["type"]
                state_record.is_running = self.clock.is_running
                state_record.speed = self.clock.speed_multiplier

                # 2. Save NPCs
                for agent in self.npcs.values():
                    npc_rec = await session.get(NPCModel, agent.id)
                    if not npc_rec:
                        npc_rec = NPCModel(id=agent.id)
                        session.add(npc_rec)

                    npc_rec.name = agent.name
                    npc_rec.age = agent.identity.age
                    npc_rec.occupation = agent.identity.occupation
                    npc_rec.personality = agent.identity.personality.model_dump()
                    npc_rec.background = agent.identity.background
                    npc_rec.interests = agent.identity.interests
                    npc_rec.skills = agent.identity.skills
                    npc_rec.beliefs = agent.identity.beliefs
                    npc_rec.personal_values = agent.identity.personal_values
                    npc_rec.goals = agent.identity.goals
                    npc_rec.x = agent.x
                    npc_rec.y = agent.y
                    npc_rec.current_location = agent.current_location
                    npc_rec.current_activity = agent.current_activity
                    npc_rec.emotion = agent.emotions.current_emotion.value
                    npc_rec.needs = agent.needs.to_dict()
                    npc_rec.wealth = agent.wealth
                    npc_rec.home_id = agent.identity.home_id
                    npc_rec.workplace_id = agent.identity.workplace_id

                    # Save Memories
                    for mem in agent.memory.memories[-20:]:
                        existing_mem = await session.get(MemoryModel, mem.id)
                        if not existing_mem:
                            db_mem = MemoryModel(
                                id=mem.id,
                                npc_id=agent.id,
                                memory_type=mem.memory_type,
                                content=mem.content,
                                importance=mem.importance,
                                sim_timestamp=mem.sim_timestamp,
                                embedding=mem.embedding
                            )
                            session.add(db_mem)

                await session.commit()
                logger.info("Successfully saved simulation checkpoint to database.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to save simulation checkpoint: {e}", exc_info=True)

    async def restore_from_db(self) -> bool:
        """Restore world state and memories from database after restart."""
        async with AsyncSessionLocal() as session:
            try:
                state_record = await session.get(SimulationStateModel, 1)
                if not state_record:
                    return False

                self.clock.tick_count = state_record.tick
                self.clock.sim_minute = state_record.sim_minute
                self.clock.sim_hour = state_record.sim_hour
                self.clock.sim_day = state_record.sim_day
                self.clock.speed_multiplier = state_record.speed

                # Load NPCs
                res = await session.execute(select(NPCModel))
                db_npcs = res.scalars().all()
                if not db_npcs:
                    return False

                for db_npc in db_npcs:
                    if db_npc.id in self.npcs:
                        agent = self.npcs[db_npc.id]
                        agent.x = db_npc.x
                        agent.y = db_npc.y
                        agent.current_location = db_npc.current_location
                        agent.current_activity = db_npc.current_activity
                        agent.wealth = db_npc.wealth
                        if db_npc.needs:
                            for k, v in db_npc.needs.items():
                                setattr(agent.needs, k, v)

                        # Load memories
                        m_res = await session.execute(select(MemoryModel).where(MemoryModel.npc_id == agent.id))
                        for db_m in m_res.scalars().all():
                            if not any(m.id == db_m.id for m in agent.memory.memories):
                                agent.memory.add_memory(
                                    content=db_m.content,
                                    sim_timestamp=db_m.sim_timestamp,
                                    memory_type=db_m.memory_type,
                                    importance=db_m.importance
                                )

                logger.info("Successfully restored simulation state from database.")
                return True
            except Exception as e:
                logger.error(f"Error restoring from database: {e}", exc_info=True)
                return False

    def get_full_state(self) -> Dict[str, Any]:
        return {
            "clock": self.clock.get_state(),
            "weather": self.weather.get_state(),
            "npcs": [agent.to_dict() for agent in self.npcs.values()],
            "parties": [p.to_dict() for p in party_manager.get_all_parties()],
            "recent_events": event_bus.get_recent_history(limit=25),
            "recent_conversations": [c.to_dict() for c in self.active_conversations[-5:]],
            "stats": self.stats
        }

# Global singleton simulation engine
sim_engine = SimulationEngine()
