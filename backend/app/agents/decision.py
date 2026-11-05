from typing import Dict, Any, List, Optional
from app.core.actions import ActionRegistry, SimulationAction, ActionType
from app.ai import get_ai_provider

class DecisionEngine:
    @staticmethod
    async def decide_action(
        npc_state: Dict[str, Any],
        current_situation: Dict[str, Any],
        current_plan_step: Optional[Dict[str, Any]],
        needs: Dict[str, float],
        emotion: str,
        recent_memories: List[Dict[str, Any]],
        nearby_npcs: List[Dict[str, Any]],
        known_locations: List[str]
    ) -> SimulationAction:
        """Evaluate situation and decide on a validated simulation action."""
        ai = get_ai_provider()
        
        # 1. Ask AI provider for next action
        decision_output = await ai.decide_next_action(
            npc_data=npc_state,
            current_situation=current_situation,
            current_plan_step=current_plan_step,
            needs=needs,
            emotion=emotion,
            recent_memories=recent_memories,
            nearby_npcs=nearby_npcs
        )
        
        proposed_action = decision_output.action
        
        # 2. Strict simulation validation
        validation = ActionRegistry.validate_action(
            action=proposed_action,
            npc_state=npc_state,
            known_locations=known_locations
        )
        
        if validation.is_valid and validation.sanitized_action:
            return validation.sanitized_action

        # 3. Safe fallback if proposed action is rejected or invalid
        home = npc_state.get("home_id", "home_1")
        if current_plan_step and current_plan_step.get("location") in known_locations:
            return SimulationAction(
                action_type=ActionType.MOVE_TO,
                target_location=current_plan_step.get("location"),
                duration_minutes=30,
                description=f"Proceeding with scheduled: {current_plan_step.get('activity')}"
            )
            
        return SimulationAction(
            action_type=ActionType.RELAX,
            target_location=npc_state.get("current_location", home),
            duration_minutes=20,
            description="Relaxing in place"
        )

