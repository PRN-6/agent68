from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.core.actions import SimulationAction

class PlanStep(BaseModel):
    start_hour: int
    start_minute: int = 0
    duration_minutes: int
    activity: str
    location: str
    description: str

class DailyPlan(BaseModel):
    date: str
    summary: str
    steps: List[PlanStep]

class DecisionOutput(BaseModel):
    thought: str
    action: SimulationAction
    emotion_update: Optional[str] = None

class DialogueTurnOutput(BaseModel):
    thought: str
    utterance: str
    end_conversation: bool = False
    sentiment: float = 0.0  # -1.0 to 1.0

class ReflectionOutput(BaseModel):
    insights: List[str]
    new_beliefs: List[str]
    supporting_memory_ids: List[str]

class LLMProvider(ABC):
    @abstractmethod
    async def generate_daily_plan(
        self,
        npc_data: Dict[str, Any],
        date_str: str,
        current_needs: Dict[str, float]
    ) -> DailyPlan:
        pass

    @abstractmethod
    async def decide_next_action(
        self,
        npc_data: Dict[str, Any],
        current_situation: Dict[str, Any],
        current_plan_step: Optional[Dict[str, Any]],
        needs: Dict[str, float],
        emotion: str,
        recent_memories: List[Dict[str, Any]],
        nearby_npcs: List[Dict[str, Any]]
    ) -> DecisionOutput:
        pass

    @abstractmethod
    async def generate_dialogue_turn(
        self,
        speaker_data: Dict[str, Any],
        listener_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        topic: str,
        relationship_data: Dict[str, Any]
    ) -> DialogueTurnOutput:
        pass

    @abstractmethod
    async def generate_reflection(
        self,
        npc_data: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> ReflectionOutput:
        pass

    @abstractmethod
    async def replan_on_event(
        self,
        npc_data: Dict[str, Any],
        current_plan: List[Dict[str, Any]],
        event_description: str,
        current_needs: Dict[str, float]
    ) -> DailyPlan:
        pass

