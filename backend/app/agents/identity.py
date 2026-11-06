from typing import List, Dict, Any
from pydantic import BaseModel, Field

class BigFivePersonality(BaseModel):
    openness: float = Field(0.5, ge=0.0, le=1.0)
    conscientiousness: float = Field(0.5, ge=0.0, le=1.0)
    extraversion: float = Field(0.5, ge=0.0, le=1.0)
    agreeableness: float = Field(0.5, ge=0.0, le=1.0)
    neuroticism: float = Field(0.5, ge=0.0, le=1.0)

class NPCIdentity(BaseModel):
    id: str
    name: str
    age: int
    occupation: str
    personality: BigFivePersonality
    background: str
    interests: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    beliefs: List[str] = Field(default_factory=list)
    personal_values: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    home_id: str
    workplace_id: str
    avatar_color: str = "#3B82F6"
    sprite_name: str = "Klaus_Mueller"  # Matches Stanford sprite sheets in assets/characters/

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
