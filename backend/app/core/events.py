import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class WorldEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # social, economic, weather, community, gossip, conflict
    description: str
    location_id: str
    initiator_id: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    sim_timestamp: int  # minute
    significance: float = 5.0  # 1 to 10
    observed_by: List[str] = Field(default_factory=list)

class EventBus:
    def __init__(self):
        self.history: List[WorldEvent] = []
        self.subscribers: List[Any] = []
        self.recent_events_limit: int = 100

    def publish_event(
        self,
        event_type: str,
        description: str,
        location_id: str,
        sim_timestamp: int,
        initiator_id: Optional[str] = None,
        participants: Optional[List[str]] = None,
        significance: float = 5.0,
        present_npc_ids: Optional[List[str]] = None
    ) -> WorldEvent:
        """Publish a new world event with strictly scoped observer lists."""
        parts = participants or []
        observers = list(set((present_npc_ids or []) + parts))
        if initiator_id and initiator_id not in observers:
            observers.append(initiator_id)
            
        event = WorldEvent(
            event_type=event_type,
            description=description,
            location_id=location_id,
            initiator_id=initiator_id,
            participants=parts,
            sim_timestamp=sim_timestamp,
            significance=significance,
            observed_by=observers
        )
        
        self.history.append(event)
        return event

    def get_events_observed_by(self, npc_id: str, since_minute: int = 0) -> List[WorldEvent]:
        """Epistemic filtering: returns ONLY events that this NPC witnessed."""
        return [
            ev for ev in self.history
            if ev.sim_timestamp >= since_minute and npc_id in ev.observed_by
        ]

    def get_recent_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [ev.model_dump() for ev in self.history[-limit:]]

event_bus = EventBus()
