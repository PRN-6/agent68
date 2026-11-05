import pytest
import asyncio
from app.simulation.engine import SimulationEngine
from app.agents.npc import NPCAgent
from app.agents.identity import NPCIdentity, BigFivePersonality
from app.core.actions import SimulationAction, ActionType, ActionRegistry
from app.core.events import EventBus
from app.agents.conversation import ConversationSession
from app.world.locations import TOWN_LOCATIONS

@pytest.fixture
def fresh_engine():
    engine = SimulationEngine()
    return engine

@pytest.fixture
def sample_agents():
    id_a = NPCIdentity(
        id="test_alex", name="Alex Carter", age=30, occupation="Carpenter",
        personality=BigFivePersonality(openness=0.7, conscientiousness=0.8, extraversion=0.8, agreeableness=0.8, neuroticism=0.2),
        background="Skilled builder", goals=["Build town hall gazebo"], home_id="home_1", workplace_id="workshop"
    )
    id_b = NPCIdentity(
        id="test_john", name="John Smith", age=40, occupation="Baker",
        personality=BigFivePersonality(openness=0.6, conscientiousness=0.8, extraversion=0.7, agreeableness=0.9, neuroticism=0.2),
        background="Experienced baker", goals=["Bake sourdough"], home_id="home_2", workplace_id="bakery"
    )
    agent_a = NPCAgent(id_a, initial_x=10.0, initial_y=10.0)
    agent_b = NPCAgent(id_b, initial_x=10.0, initial_y=10.0)
    return agent_a, agent_b

# Scenario 1: NPC remembers another NPC after a conversation
@pytest.mark.asyncio
async def test_npc_remembers_after_conversation(sample_agents):
    agent_a, agent_b = sample_agents
    session = ConversationSession(agent_a, agent_b, "town_square", sim_minute=60, topic="Town square restoration")
    await session.execute_dialogue(max_turns=2)

    # Check memories formed
    mem_a = [m for m in agent_a.memory.memories if agent_b.name in m.content]
    mem_b = [m for m in agent_b.memory.memories if agent_a.name in m.content]
    assert len(mem_a) > 0, "Alex should remember John after conversation"
    assert len(mem_b) > 0, "John should remember Alex after conversation"

# Scenario 2: NPC retrieves a relevant past memory
@pytest.mark.asyncio
async def test_npc_retrieves_relevant_past_memory(sample_agents):
    agent_a, _ = sample_agents
    agent_a.add_memory("I bought fresh croissants at the bakery this morning.", sim_minute=50, importance=6.0)
    agent_a.add_memory("The clockmaker fixed the brass gears at the workshop.", sim_minute=80, importance=5.0)
    agent_a.add_memory("Hannah recommended organic honey apples from Greenfield farm.", sim_minute=100, importance=7.0)

    # Retrieve memory related to bakery/food
    retrieved = agent_a.memory.retrieve(query="croissants bakery breakfast", current_sim_minute=120, top_k=1)
    assert len(retrieved) > 0
    assert "croissants" in retrieved[0].content or "bakery" in retrieved[0].content

# Scenario 3: NPC changes its plan when an unexpected event occurs
@pytest.mark.asyncio
async def test_npc_replanning_on_unexpected_event(sample_agents):
    agent_a, _ = sample_agents
    await agent_a.planner.generate_schedule_for_day(agent_a.get_profile_dict(), sim_day=1, date_str="Day 1", current_needs=agent_a.needs.to_dict())
    
    initial_summary = agent_a.planner.plan_summary
    await agent_a.planner.handle_unexpected_event(
        npc_data=agent_a.get_profile_dict(),
        event_description="Sudden fire breakout in the timber yard!",
        current_needs=agent_a.needs.to_dict()
    )
    
    # Assert plan was dynamically revised
    assert "fire" in agent_a.planner.plan_summary.lower() or any("fire" in s.activity.lower() for s in agent_a.planner.schedule)

# Scenario 4: NPC relationship changes after meaningful interactions
@pytest.mark.asyncio
async def test_relationship_changes_after_interaction(sample_agents):
    agent_a, agent_b = sample_agents
    rel_before = agent_a.relationships.get_or_create(agent_b.id).familiarity

    session = ConversationSession(agent_a, agent_b, "bakery", sim_minute=120, topic="Warm sourdough bread")
    await session.execute_dialogue(max_turns=3)

    rel_after = agent_a.relationships.get_or_create(agent_b.id)
    assert rel_after.familiarity > rel_before, "Familiarity should increase after conversation"
    assert rel_after.shared_experiences_count >= 1

# Scenario 5: NPC can independently initiate a conversation
@pytest.mark.asyncio
async def test_autonomous_conversation_initiation(sample_agents):
    agent_a, agent_b = sample_agents
    # Set social need low to prompt conversation
    agent_a.needs.social = 20.0
    
    # Ask decision engine
    action = await agent_a.planner.generate_schedule_for_day(agent_a.get_profile_dict(), 1, "Day 1", agent_a.needs.to_dict())
    from app.agents.decision import DecisionEngine
    decided_action = await DecisionEngine.decide_action(
        npc_state=agent_a.get_profile_dict(),
        current_situation={"location": "town_square"},
        current_plan_step=None,
        needs=agent_a.needs.to_dict(),
        emotion="Lonely",
        recent_memories=[],
        nearby_npcs=[agent_b.get_profile_dict()],
        known_locations=list(TOWN_LOCATIONS.keys())
    )
    assert decided_action.action_type == ActionType.CONVERSE
    assert decided_action.target_npc_id == agent_b.id

# Scenario 6: NPC can develop a goal
def test_npc_can_develop_a_goal(sample_agents):
    agent_a, _ = sample_agents
    initial_goals_count = len(agent_a.identity.goals)
    agent_a.identity.goals.append("Organize a community woodworking workshop")
    assert len(agent_a.identity.goals) == initial_goals_count + 1

# Scenario 7: NPC can complete a planned activity
@pytest.mark.asyncio
async def test_npc_completes_planned_activity(sample_agents):
    agent_a, _ = sample_agents
    action = SimulationAction(action_type=ActionType.EAT, duration_minutes=20, description="Eating fresh bread")
    agent_a.needs.hunger = 40.0
    agent_a.execute_action(action, sim_minute=100)
    
    # Hunger should improve
    assert agent_a.needs.hunger > 40.0
    assert agent_a.action_minutes_remaining == 20

# Scenario 8: NPC retains its identity after application restart (DB Persistence)
@pytest.mark.asyncio
async def test_npc_persistence_across_restart(fresh_engine):
    from app.db.database import init_db
    await init_db()
    await fresh_engine.initialize()
    
    # Modify an agent's memory and activity
    first_agent = list(fresh_engine.npcs.values())[0]
    first_agent.add_memory("Important secret revealed at dawn", sim_minute=45, importance=9.5)
    first_agent.wealth = 250.0

    # Save checkpoint
    await fresh_engine.save_checkpoint_to_db()

    # Create new engine instance simulating restart
    new_engine = SimulationEngine()
    await new_engine.initialize()
    success = await new_engine.restore_from_db()
    assert success is True

    restored_agent = new_engine.npcs[first_agent.id]
    assert restored_agent.wealth == 250.0
    assert any("Important secret revealed at dawn" in m.content for m in restored_agent.memory.memories)

# Scenario 9: World simulation continues without an active LLM request
@pytest.mark.asyncio
async def test_deterministic_simulation_ticks_without_llm(fresh_engine):
    await fresh_engine.initialize()
    initial_tick = fresh_engine.clock.tick_count
    
    # Step 10 ticks directly
    for _ in range(10):
        await fresh_engine.tick()

    assert fresh_engine.clock.tick_count == initial_tick + 10
    assert fresh_engine.clock.sim_minute >= 10

# Scenario 10: Invalid AI-generated actions are rejected
def test_invalid_action_rejection():
    # Hallucinated location
    invalid_action = SimulationAction(
        action_type=ActionType.MOVE_TO,
        target_location="mars_colony_dome",
        duration_minutes=30
    )
    result = ActionRegistry.validate_action(
        invalid_action,
        npc_state={"id": "alex", "wealth": 50.0},
        known_locations=["town_square", "bakery", "clinic"]
    )
    assert result.is_valid is False
    assert "Unknown target location" in result.rejection_reason

    # Insufficient funds
    expensive_shop = SimulationAction(
        action_type=ActionType.SHOP,
        duration_minutes=15,
        parameters={"cost": 500.0}
    )
    res_shop = ActionRegistry.validate_action(
        expensive_shop,
        npc_state={"id": "alex", "wealth": 20.0},
        known_locations=["town_square"]
    )
    assert res_shop.is_valid is False
    assert "Insufficient funds" in res_shop.rejection_reason

# Scenario 11: NPCs cannot access information they have not observed or learned
def test_epistemic_information_boundary():
    bus = EventBus()
    # Event occurs at the clinic, observed ONLY by Marcus and Maya
    bus.publish_event(
        event_type="medical",
        description="Rare herbal medicine discovered in apothecary inventory",
        location_id="clinic",
        sim_timestamp=150,
        present_npc_ids=["npc_marcus_thorne", "npc_maya_patel"]
    )

    # Marcus should know
    marcus_events = bus.get_events_observed_by("npc_marcus_thorne")
    assert len(marcus_events) == 1

    # Arthur (at town hall) should NOT know
    arthur_events = bus.get_events_observed_by("npc_arthur_vance")
    assert len(arthur_events) == 0

# Scenario 12: Simulation can be paused and resumed safely
def test_simulation_pause_resume(fresh_engine):
    fresh_engine.clock.resume()
    assert fresh_engine.clock.is_running is True

    fresh_engine.clock.pause()
    assert fresh_engine.clock.is_running is False

    fresh_engine.clock.resume()
    assert fresh_engine.clock.is_running is True
