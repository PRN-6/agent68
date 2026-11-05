from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class RelationshipEdge(BaseModel):
    source_npc_id: str
    target_npc_id: str
    familiarity: float = Field(default=10.0, ge=0.0, le=100.0)
    trust: float = Field(default=50.0, ge=0.0, le=100.0)
    affinity: float = Field(default=50.0, ge=0.0, le=100.0)
    respect: float = Field(default=50.0, ge=0.0, le=100.0)
    conflict: float = Field(default=0.0, ge=0.0, le=100.0)
    shared_experiences_count: int = 0
    relationship_type: str = "Acquaintance"
    last_interaction_minute: int = 0

    def update_after_interaction(self, sentiment: float, topic: str, sim_minute: int):
        """Update relationship attributes based on interaction sentiment (-1.0 to 1.0)."""
        self.shared_experiences_count += 1
        self.last_interaction_minute = sim_minute
        
        # Increase familiarity with every interaction
        self.familiarity = min(100.0, self.familiarity + 5.0)

        if sentiment > 0.1:
            self.trust = min(100.0, self.trust + sentiment * 4.0)
            self.affinity = min(100.0, self.affinity + sentiment * 5.0)
            self.respect = min(100.0, self.respect + sentiment * 3.0)
            self.conflict = max(0.0, self.conflict - 2.0)
        elif sentiment < -0.1:
            self.trust = max(0.0, self.trust + sentiment * 5.0)
            self.affinity = max(0.0, self.affinity + sentiment * 6.0)
            self.conflict = min(100.0, self.conflict + abs(sentiment) * 8.0)

        # Categorize
        if self.conflict > 60.0:
            self.relationship_type = "Rival"
        elif self.affinity > 80.0 and self.trust > 75.0:
            self.relationship_type = "Close Friend"
        elif self.affinity > 60.0 and self.trust > 55.0:
            self.relationship_type = "Friend"
        elif self.familiarity > 30.0:
            self.relationship_type = "Acquaintance"
        else:
            self.relationship_type = "Stranger"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_npc_id": self.source_npc_id,
            "target_npc_id": self.target_npc_id,
            "familiarity": round(self.familiarity, 1),
            "trust": round(self.trust, 1),
            "affinity": round(self.affinity, 1),
            "respect": round(self.respect, 1),
            "conflict": round(self.conflict, 1),
            "shared_experiences_count": self.shared_experiences_count,
            "relationship_type": self.relationship_type,
            "last_interaction_minute": self.last_interaction_minute
        }

class RelationshipManager:
    def __init__(self, npc_id: str):
        self.npc_id = npc_id
        self.relationships: Dict[str, RelationshipEdge] = {}

    def get_or_create(self, target_npc_id: str, default_type: str = "Acquaintance") -> RelationshipEdge:
        if target_npc_id not in self.relationships:
            self.relationships[target_npc_id] = RelationshipEdge(
                source_npc_id=self.npc_id,
                target_npc_id=target_npc_id,
                relationship_type=default_type
            )
        return self.relationships[target_npc_id]

    def record_interaction(self, target_npc_id: str, sentiment: float, topic: str, sim_minute: int):
        rel = self.get_or_create(target_npc_id)
        rel.update_after_interaction(sentiment, topic, sim_minute)

    def get_all(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.relationships.values()]

