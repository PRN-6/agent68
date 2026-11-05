from typing import Dict, Any
from pydantic import BaseModel, Field

class NPCNeeds(BaseModel):
    energy: float = Field(default=85.0, ge=0.0, le=100.0)
    hunger: float = Field(default=80.0, ge=0.0, le=100.0)
    social: float = Field(default=75.0, ge=0.0, le=100.0)
    fun: float = Field(default=70.0, ge=0.0, le=100.0)
    hygiene: float = Field(default=90.0, ge=0.0, le=100.0)
    purpose: float = Field(default=80.0, ge=0.0, le=100.0)

    def tick_decay(self, minutes_passed: int = 1, current_activity: str = "Idle") -> Dict[str, float]:
        """Deterministic decay of biological and psychological needs over time."""
        is_sleeping = "sleep" in current_activity.lower() or "rest" in current_activity.lower()
        is_eating = "eat" in current_activity.lower() or "lunch" in current_activity.lower() or "breakfast" in current_activity.lower()
        is_socializing = "converse" in current_activity.lower() or "social" in current_activity.lower()
        is_working = "work" in current_activity.lower()

        # Energy
        if is_sleeping:
            self.energy = min(100.0, self.energy + 0.3 * minutes_passed)
        else:
            self.energy = max(0.0, self.energy - 0.06 * minutes_passed)

        # Hunger
        if is_eating:
            self.hunger = min(100.0, self.hunger + 1.5 * minutes_passed)
        else:
            self.hunger = max(0.0, self.hunger - 0.08 * minutes_passed)

        # Social
        if is_socializing:
            self.social = min(100.0, self.social + 1.2 * minutes_passed)
        else:
            self.social = max(0.0, self.social - 0.04 * minutes_passed)

        # Fun
        if "relax" in current_activity.lower() or "hobby" in current_activity.lower():
            self.fun = min(100.0, self.fun + 0.8 * minutes_passed)
        else:
            self.fun = max(0.0, self.fun - 0.03 * minutes_passed)

        # Purpose
        if is_working:
            self.purpose = min(100.0, self.purpose + 0.4 * minutes_passed)
        else:
            self.purpose = max(0.0, self.purpose - 0.02 * minutes_passed)

        return self.to_dict()

    def satisfy(self, need_name: str, amount: float):
        if hasattr(self, need_name):
            current = getattr(self, need_name)
            setattr(self, need_name, min(100.0, max(0.0, current + amount)))

    def get_most_urgent_need(self) -> str:
        values = {
            "energy": self.energy,
            "hunger": self.hunger,
            "social": self.social,
            "fun": self.fun,
            "hygiene": self.hygiene,
            "purpose": self.purpose
        }
        return min(values, key=values.get)

    def to_dict(self) -> Dict[str, float]:
        return {
            "energy": round(self.energy, 1),
            "hunger": round(self.hunger, 1),
            "social": round(self.social, 1),
            "fun": round(self.fun, 1),
            "hygiene": round(self.hygiene, 1),
            "purpose": round(self.purpose, 1),
        }
