import json
import logging
from typing import Dict, Any, List, Optional
from app.ai.provider import LLMProvider, DailyPlan, PlanStep, DecisionOutput, DialogueTurnOutput, ReflectionOutput
from app.ai.mock_provider import DeterministicMockProvider
from app.core.actions import SimulationAction, ActionType
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    """Google Gemini API Provider with structured JSON responses and graceful fallback."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model
        self.fallback = DeterministicMockProvider()
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize google-genai client: {e}. Falling back to mock provider.")

    async def generate_daily_plan(
        self,
        npc_data: Dict[str, Any],
        date_str: str,
        current_needs: Dict[str, float]
    ) -> DailyPlan:
        if not self.client:
            return await self.fallback.generate_daily_plan(npc_data, date_str, current_needs)

        prompt = f"""You are generating a daily plan for an NPC in an autonomous society simulation.
NPC Profile:
Name: {npc_data.get('name')}
Age: {npc_data.get('age')}
Occupation: {npc_data.get('occupation')}
Personality: {npc_data.get('personality')}
Background: {npc_data.get('background')}
Current Needs: {current_needs}
Locations available: home, clinic, bakery, tavern, marketplace, library, town_hall, workshop, park, farm, town_square.

Output STRICT JSON matching this schema:
{{
  "date": "{date_str}",
  "summary": "Brief summary of the day's intent",
  "steps": [
    {{
      "start_hour": 7,
      "start_minute": 0,
      "duration_minutes": 60,
      "activity": "Morning routine",
      "location": "{npc_data.get('home_id')}",
      "description": "Wake up and breakfast"
    }}
  ]
}}
Ensure the entire day from 7:00 to 22:00 is covered with realistic activities.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            steps = [PlanStep(**s) for s in data.get("steps", [])]
            return DailyPlan(date=data.get("date", date_str), summary=data.get("summary", ""), steps=steps)
        except Exception as e:
            logger.error(f"Gemini generate_daily_plan error: {e}. Using fallback.")
            return await self.fallback.generate_daily_plan(npc_data, date_str, current_needs)

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
        if not self.client:
            return await self.fallback.decide_next_action(npc_data, current_situation, current_plan_step, needs, emotion, recent_memories, nearby_npcs)

        prompt = f"""Decide the next action for NPC {npc_data.get('name')} ({npc_data.get('occupation')}).
Current Location: {npc_data.get('current_location')}
Current Needs: {needs}
Emotional State: {emotion}
Current Scheduled Step: {current_plan_step}
Nearby NPCs: {[n.get('name') for n in nearby_npcs]}
Recent Memories: {[m.get('content') for m in recent_memories[:3]]}

Valid Action Types: MOVE_TO, WORK, EAT, REST, SOCIALIZE, CONVERSE, SHOP, REFLECT, RELAX.
Output STRICT JSON:
{{
  "thought": "Internal reasoning for why this action makes sense",
  "action": {{
    "action_type": "MOVE_TO | WORK | EAT | REST | CONVERSE | RELAX",
    "target_location": "location_id if moving",
    "target_npc_id": "npc_id if conversing",
    "duration_minutes": 30,
    "description": "Short description of what the NPC is doing"
  }},
  "emotion_update": "New emotion (Happy, Relaxed, Focused, etc.)"
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            action_data = data.get("action", {})
            action = SimulationAction(
                action_type=ActionType(action_data.get("action_type", "RELAX")),
                target_location=action_data.get("target_location"),
                target_npc_id=action_data.get("target_npc_id"),
                duration_minutes=int(action_data.get("duration_minutes", 30)),
                description=action_data.get("description", "")
            )
            return DecisionOutput(thought=data.get("thought", ""), action=action, emotion_update=data.get("emotion_update"))
        except Exception as e:
            logger.error(f"Gemini decide_next_action error: {e}. Using fallback.")
            return await self.fallback.decide_next_action(npc_data, current_situation, current_plan_step, needs, emotion, recent_memories, nearby_npcs)

    async def generate_dialogue_turn(
        self,
        speaker_data: Dict[str, Any],
        listener_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        topic: str,
        relationship_data: Dict[str, Any]
    ) -> DialogueTurnOutput:
        if not self.client:
            return await self.fallback.generate_dialogue_turn(speaker_data, listener_data, conversation_history, topic, relationship_data)

        prompt = f"""Generate dialogue in an autonomous town simulation.
Speaker: {speaker_data.get('name')} ({speaker_data.get('occupation')}), Personality: {speaker_data.get('personality')}
Listener: {listener_data.get('name')} ({listener_data.get('occupation')})
Topic: {topic}
Relationship: Familiarity={relationship_data.get('familiarity')}, Trust={relationship_data.get('trust')}
Conversation History so far:
{conversation_history}

Output STRICT JSON:
{{
  "thought": "Internal conversational intent",
  "utterance": "What the speaker says aloud",
  "end_conversation": false,
  "sentiment": 0.5
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            return DialogueTurnOutput(**data)
        except Exception as e:
            logger.error(f"Gemini generate_dialogue_turn error: {e}. Using fallback.")
            return await self.fallback.generate_dialogue_turn(speaker_data, listener_data, conversation_history, topic, relationship_data)

    async def generate_reflection(
        self,
        npc_data: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> ReflectionOutput:
        if not self.client:
            return await self.fallback.generate_reflection(npc_data, memories)

        prompt = f"""Synthesize high-level reflections and beliefs from recent memories for {npc_data.get('name')}.
Recent Memories:
{[m.get('content') for m in memories]}

Output STRICT JSON:
{{
  "insights": ["High-level insight 1", "Insight 2"],
  "new_beliefs": ["Belief about world or person 1", "Belief 2"],
  "supporting_memory_ids": {[m.get('id') for m in memories[:5]]}
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            return ReflectionOutput(**data)
        except Exception as e:
            logger.error(f"Gemini generate_reflection error: {e}. Using fallback.")
            return await self.fallback.generate_reflection(npc_data, memories)

    async def replan_on_event(
        self,
        npc_data: Dict[str, Any],
        current_plan: List[Dict[str, Any]],
        event_description: str,
        current_needs: Dict[str, float]
    ) -> DailyPlan:
        return await self.fallback.replan_on_event(npc_data, current_plan, event_description, current_needs)
