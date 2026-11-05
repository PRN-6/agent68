from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    MOVE_TO = "MOVE_TO"
    WORK = "WORK"
    EAT = "EAT"
    REST = "REST"
    SOCIALIZE = "SOCIALIZE"
    CONVERSE = "CONVERSE"
    SHOP = "SHOP"
    REFLECT = "REFLECT"
    ATTEND_EVENT = "ATTEND_EVENT"
    RELAX = "RELAX"
    IDLE = "IDLE"

class SimulationAction(BaseModel):
    action_type: ActionType
    target_location: Optional[str] = None
    target_npc_id: Optional[str] = None
    duration_minutes: int = Field(default=30, ge=1, le=480)
    description: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)

class ActionValidationResult(BaseModel):
    is_valid: bool
    sanitized_action: Optional[SimulationAction] = None
    rejection_reason: Optional[str] = None

class ActionRegistry:
    @staticmethod
    def validate_action(
        action: SimulationAction,
        npc_state: Dict[str, Any],
        known_locations: List[str]
    ) -> ActionValidationResult:
        """Strictly validate proposed agent action against simulation rules."""
        
        # 1. MOVE_TO validation
        if action.action_type == ActionType.MOVE_TO:
            if not action.target_location or action.target_location not in known_locations:
                return ActionValidationResult(
                    is_valid=False,
                    rejection_reason=f"Unknown target location '{action.target_location}'."
                )
            return ActionValidationResult(is_valid=True, sanitized_action=action)
            
        # 2. CONVERSE & SOCIALIZE validation
        elif action.action_type in (ActionType.CONVERSE, ActionType.SOCIALIZE):
            if not action.target_npc_id:
                return ActionValidationResult(
                    is_valid=False,
                    rejection_reason="Target NPC ID required for conversation/socialize."
                )
            if action.target_npc_id == npc_state.get("id"):
                return ActionValidationResult(
                    is_valid=False,
                    rejection_reason="NPC cannot initiate conversation with themselves."
                )
            return ActionValidationResult(is_valid=True, sanitized_action=action)
            
        # 3. WORK validation
        elif action.action_type == ActionType.WORK:
            # Duration check
            action.duration_minutes = max(15, min(action.duration_minutes, 240))
            return ActionValidationResult(is_valid=True, sanitized_action=action)
            
        # 4. REST validation
        elif action.action_type == ActionType.REST:
            action.duration_minutes = max(10, min(action.duration_minutes, 480))
            return ActionValidationResult(is_valid=True, sanitized_action=action)
            
        # 5. EAT validation
        elif action.action_type == ActionType.EAT:
            action.duration_minutes = max(10, min(action.duration_minutes, 60))
            return ActionValidationResult(is_valid=True, sanitized_action=action)
            
        # 6. SHOP validation
        elif action.action_type == ActionType.SHOP:
            cost = float(action.parameters.get("cost", 5.0))
            if npc_state.get("wealth", 0.0) < cost:
                return ActionValidationResult(
                    is_valid=False,
                    rejection_reason=f"Insufficient funds: NPC has {npc_state.get('wealth')}, item costs {cost}."
                )
            return ActionValidationResult(is_valid=True, sanitized_action=action)

        # 7. REFLECT, RELAX, ATTEND_EVENT, IDLE
        elif action.action_type in (ActionType.REFLECT, ActionType.RELAX, ActionType.ATTEND_EVENT, ActionType.IDLE):
            action.duration_minutes = max(5, min(action.duration_minutes, 120))
            return ActionValidationResult(is_valid=True, sanitized_action=action)

        return ActionValidationResult(
            is_valid=False,
            rejection_reason=f"Unsupported action type: {action.action_type}"
        )
