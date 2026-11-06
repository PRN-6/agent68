import math
from typing import Dict, Any, List, Optional, Tuple
from app.agents.identity import NPCIdentity
from app.agents.needs import NPCNeeds
from app.agents.emotions import EmotionalState, EmotionType
from app.agents.memory import MemoryStream, MemoryItem
from app.agents.planning import Planner, ScheduleItem
from app.agents.relationships import RelationshipManager
from app.agents.decision import DecisionEngine
from app.agents.reflection import ReflectionEngine
from app.core.actions import SimulationAction, ActionType
from app.world.pathfinding import find_path
from app.world.locations import get_location

class NPCAgent:
    def __init__(self, identity: NPCIdentity, initial_x: float = 0.0, initial_y: float = 0.0):
        self.identity = identity
        self.id = identity.id
        self.name = identity.name
        self.x = initial_x
        self.y = initial_y
        self.current_location = identity.home_id
        
        self.needs = NPCNeeds()
        self.emotions = EmotionalState()
        self.memory = MemoryStream(self.id)
        self.planner = Planner(self.id)
        self.relationships = RelationshipManager(self.id)
        
        # Action & Movement State
        self.current_action: Optional[SimulationAction] = None
        self.current_activity: str = "Waking up"
        self.action_minutes_remaining: int = 0
        self.path_queue: List[Tuple[float, float]] = []
        self.wealth: float = 120.0
        self.last_decision_minute: int = -1

    def get_profile_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.identity.age,
            "occupation": self.identity.occupation,
            "personality": self.identity.personality.model_dump(),
            "background": self.identity.background,
            "interests": self.identity.interests,
            "skills": self.identity.skills,
            "beliefs": self.identity.beliefs,
            "personal_values": self.identity.personal_values,
            "goals": self.identity.goals,
            "home_id": self.identity.home_id,
            "workplace_id": self.identity.workplace_id,
            "avatar_color": self.identity.avatar_color,
            "sprite_name": getattr(self.identity, "sprite_name", "Klaus_Mueller"),
            "current_location": self.current_location,
            "wealth": self.wealth
        }

    def add_memory(self, content: str, sim_minute: int, memory_type: str = "short_term", importance: float = 5.0) -> MemoryItem:
        return self.memory.add_memory(content, sim_minute, memory_type, importance)

    def set_destination(self, target_x: float, target_y: float):
        self.path_queue = find_path((self.x, self.y), (target_x, target_y))

    def move_towards_target(self, speed: float = 0.5) -> bool:
        """Step along waypoint path towards current target destination."""
        if not self.path_queue:
            return True  # Arrived

        target = self.path_queue[0]
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist <= speed:
            self.x = target[0]
            self.y = target[1]
            self.path_queue.pop(0)
            return len(self.path_queue) == 0
        else:
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            return False

    async def update_tick(
        self,
        sim_minute: int,
        sim_hour: int,
        sim_day: int,
        weather: Dict[str, Any],
        nearby_npcs: List[Dict[str, Any]],
        known_locations: List[str]
    ):
        """Simulation tick: handles biological needs decay, path movement, and reasoning checks."""
        # 1. Biological needs decay
        self.needs.tick_decay(minutes_passed=1, current_activity=self.current_activity)
        self.emotions.update_from_needs(self.needs.to_dict())

        # 2. Movement along path
        if self.path_queue:
            arrived = self.move_towards_target(speed=0.6)
            if arrived and self.current_action and self.current_action.target_location:
                self.current_location = self.current_action.target_location
                self.current_activity = f"At {self.current_location}"

        # 3. Decrement action duration
        if self.action_minutes_remaining > 0:
            self.action_minutes_remaining -= 1

        # 4. Check if reflection should trigger
        if ReflectionEngine.should_reflect(self.memory, sim_hour):
            await ReflectionEngine.perform_reflection(
                npc_data=self.get_profile_dict(),
                memory_stream=self.memory,
                current_sim_minute=sim_minute
            )

        # 5. Check if next action decision is needed
        # Decide if: no action, action finished, or critical need override
        urgent_hunger = self.needs.hunger < 15.0
        urgent_energy = self.needs.energy < 10.0
        
        need_decision = (
            self.action_minutes_remaining <= 0 or
            (urgent_hunger and "eat" not in self.current_activity.lower()) or
            (urgent_energy and "sleep" not in self.current_activity.lower() and "rest" not in self.current_activity.lower())
        )

        if need_decision and (sim_minute - self.last_decision_minute >= 10 or self.last_decision_minute == -1):
            self.last_decision_minute = sim_minute
            current_step = self.planner.get_current_step(sim_hour, sim_minute % 60)
            recent_mems = [m.to_dict() for m in self.memory.retrieve(query="What should I do right now?", current_sim_minute=sim_minute, top_k=3)]
            
            action = await DecisionEngine.decide_action(
                npc_state=self.get_profile_dict(),
                current_situation={"weather": weather, "location": self.current_location},
                current_plan_step=current_step.model_dump() if current_step else None,
                needs=self.needs.to_dict(),
                emotion=self.emotions.current_emotion.value,
                recent_memories=recent_mems,
                nearby_npcs=nearby_npcs,
                known_locations=known_locations
            )

            self.execute_action(action, sim_minute)

    def execute_action(self, action: SimulationAction, sim_minute: int):
        self.current_action = action
        self.action_minutes_remaining = action.duration_minutes
        self.current_activity = action.description or action.action_type.value

        if action.action_type == ActionType.MOVE_TO and action.target_location:
            loc = get_location(action.target_location)
            if loc:
                self.set_destination(loc.x + loc.width / 2.0, loc.y + loc.height / 2.0)
                
        elif action.action_type == ActionType.EAT:
            self.needs.satisfy("hunger", 40.0)
            self.emotions.set_emotion(EmotionType.RELAXED, 0.6)
            
        elif action.action_type == ActionType.REST:
            self.needs.satisfy("energy", 30.0)
            self.emotions.set_emotion(EmotionType.RELAXED, 0.5)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.identity.age,
            "occupation": self.identity.occupation,
            "personality": self.identity.personality.model_dump(),
            "background": self.identity.background,
            "interests": self.identity.interests,
            "skills": self.identity.skills,
            "beliefs": self.identity.beliefs,
            "goals": self.identity.goals,
            "home_id": self.identity.home_id,
            "workplace_id": self.identity.workplace_id,
            "avatar_color": self.identity.avatar_color,
            "sprite_name": getattr(self.identity, "sprite_name", "Klaus_Mueller"),
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "current_location": self.current_location,
            "current_activity": self.current_activity,
            "action_minutes_remaining": self.action_minutes_remaining,
            "is_moving": len(self.path_queue) > 0,
            "needs": self.needs.to_dict(),
            "emotion": self.emotions.to_dict(),
            "wealth": round(self.wealth, 1),
            "memory_count": len(self.memory.memories),
            "plan_summary": self.planner.plan_summary,
            "current_plan_step": self.planner.get_current_step(7, 0).model_dump() if self.planner.schedule else None,
            "relationships": self.relationships.get_all()
        }
