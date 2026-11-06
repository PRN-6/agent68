import math
import random
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
from app.world.pathfinding import find_path, get_walkable_tiles_in_bounds
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
        self.wealth: float = float(getattr(identity, "gold", 120.0))
        self.last_decision_minute: int = -1
        self.micro_wander_timer: int = random.randint(10, 25)
        self.last_sim_hour: int = 7
        self.last_sim_minute: int = 0
        self._last_plan_step_key: Optional[str] = None

        # MMORPG Character Attributes
        self.rpg_class: str = getattr(identity, "rpg_class", "Warrior")
        self.role: str = getattr(identity, "role", "Melee DPS")
        self.level: int = getattr(identity, "level", 1)
        self.hp: int = getattr(identity, "hp", 100)
        self.max_hp: int = getattr(identity, "max_hp", 100)
        self.mana: int = getattr(identity, "mana", 50)
        self.max_mana: int = getattr(identity, "max_mana", 50)
        self.equipment: Dict[str, str] = getattr(identity, "equipment", {})
        self.party_id: Optional[str] = getattr(identity, "party_id", None)
        self.title: str = getattr(identity, "title", "Adventurer")
        self.dungeon_clears: int = getattr(identity, "dungeon_clears", 0)
        self.monsters_slain: int = getattr(identity, "monsters_slain", 0)

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
            "wealth": self.wealth,
            "rpg_class": self.rpg_class,
            "role": self.role,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "equipment": self.equipment,
            "party_id": self.party_id,
            "title": self.title,
            "dungeon_clears": self.dungeon_clears,
            "monsters_slain": self.monsters_slain
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

    def _perform_ambient_micro_move(self):
        """Pick a nearby walkable tile within current location to simulate lively human movement."""
        loc = get_location(self.current_location)
        if not loc:
            return
        
        walkable_tiles = get_walkable_tiles_in_bounds(loc.x, loc.y, loc.x + loc.width, loc.y + loc.height)
        if not walkable_tiles:
            return
            
        candidates = [t for t in walkable_tiles if math.hypot(t[0] - self.x, t[1] - self.y) >= 1.5]
        if candidates:
            target = random.choice(candidates)
            self.set_destination(float(target[0]), float(target[1]))

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
        self.last_sim_hour = sim_hour
        self.last_sim_minute = sim_minute

        # 1. Biological needs decay & Passive RPG Regeneration
        self.needs.tick_decay(minutes_passed=1, current_activity=self.current_activity)
        self.emotions.update_from_needs(self.needs.to_dict())

        # Passive HP and Mana regeneration when resting, sleeping, or in tavern/inn
        if "rest" in self.current_activity.lower() or "sleep" in self.current_activity.lower() or self.current_location in ["tavern", "inn", "guild_hall"]:
            if self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 2)
            if self.mana < self.max_mana:
                self.mana = min(self.max_mana, self.mana + 3)

        # 2. Movement along path
        if self.path_queue:
            arrived = self.move_towards_target(speed=0.6)
            if arrived and self.current_action and self.current_action.action_type == ActionType.MOVE_TO:
                if self.current_action.target_location:
                    self.current_location = self.current_action.target_location
                    self.current_activity = f"At {self.current_location}"
                # Arrived at travel destination: clear remaining move delay to transition to next activity immediately
                self.action_minutes_remaining = 0

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

        # 5. Check if scheduled plan step changed
        current_step = self.planner.get_current_step(sim_hour, sim_minute % 60)
        step_changed = False
        if current_step:
            step_key = f"{current_step.start_hour}:{current_step.start_minute}_{current_step.location}"
            if self._last_plan_step_key != step_key:
                if self._last_plan_step_key is not None:
                    # New schedule block started!
                    if current_step.location != self.current_location:
                        step_changed = True
                self._last_plan_step_key = step_key

        # 6. Check if next action decision is needed
        urgent_hunger = self.needs.hunger < 15.0
        urgent_energy = self.needs.energy < 10.0
        
        need_decision = (
            step_changed or
            self.action_minutes_remaining <= 0 or
            (urgent_hunger and "eat" not in self.current_activity.lower()) or
            (urgent_energy and "sleep" not in self.current_activity.lower() and "rest" not in self.current_activity.lower())
        )

        if need_decision and (step_changed or sim_minute - self.last_decision_minute >= 5 or self.last_decision_minute == -1):
            self.last_decision_minute = sim_minute
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

        # 7. Ambient Micro-Wandering:
        # If not moving along a path and not sleeping/resting, occasionally wander to an interior tile
        # to ensure the town feels alive and dynamic instead of static
        if not self.path_queue and "sleep" not in self.current_activity.lower() and "rest" not in self.current_activity.lower():
            self.micro_wander_timer -= 1
            if self.micro_wander_timer <= 0:
                self.micro_wander_timer = random.randint(15, 30)
                self._perform_ambient_micro_move()

    def execute_action(self, action: SimulationAction, sim_minute: int):
        self.current_action = action
        self.action_minutes_remaining = action.duration_minutes
        self.current_activity = action.description or action.action_type.value

        if action.action_type == ActionType.MOVE_TO and action.target_location:
            loc = get_location(action.target_location)
            if loc:
                self.set_destination(loc.walk_x, loc.walk_y)
                
        elif action.action_type == ActionType.EAT:
            self.needs.satisfy("hunger", 45.0)
            self.emotions.set_emotion(EmotionType.RELAXED, 0.7)
            
        elif action.action_type == ActionType.REST:
            self.needs.satisfy("energy", 35.0)
            self.emotions.set_emotion(EmotionType.RELAXED, 0.6)

        elif action.action_type == ActionType.CONVERSE:
            self.needs.satisfy("social", 40.0)
            self.emotions.set_emotion(EmotionType.HAPPY, 0.7)

        elif action.action_type == ActionType.WORK:
            self.wealth += 5.0
            self.emotions.set_emotion(EmotionType.CURIOUS, 0.6)

        elif action.action_type == ActionType.RELAX:
            self.needs.satisfy("fun", 25.0)
            self.needs.satisfy("energy", 10.0)
            self.emotions.set_emotion(EmotionType.RELAXED, 0.6)

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
            "rpg_class": self.rpg_class,
            "role": self.role,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "equipment": self.equipment,
            "party_id": self.party_id,
            "title": self.title,
            "dungeon_clears": self.dungeon_clears,
            "monsters_slain": self.monsters_slain,
            "memory_count": len(self.memory.memories),
            "plan_summary": self.planner.plan_summary,
            "current_plan_step": self.planner.get_current_step(getattr(self, "last_sim_hour", 7), getattr(self, "last_sim_minute", 0)).model_dump() if self.planner.schedule else None,
            "relationships": self.relationships.get_all()
        }
