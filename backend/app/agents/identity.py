from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

class BigFivePersonality(BaseModel):
    openness: float = Field(0.5, ge=0.0, le=1.0)
    conscientiousness: float = Field(0.5, ge=0.0, le=1.0)
    extraversion: float = Field(0.5, ge=0.0, le=1.0)
    agreeableness: float = Field(0.5, ge=0.0, le=1.0)
    neuroticism: float = Field(0.5, ge=0.0, le=1.0)

class RPGClass(str, Enum):
    PALADIN = "Paladin"
    WARRIOR = "Warrior"
    MAGE = "Mage"
    CLERIC = "Cleric"
    ROGUE = "Rogue"
    RANGER = "Ranger"
    ALCHEMIST = "Alchemist"
    BLACKSMITH = "Blacksmith"
    GUILDMASTER = "Guildmaster"
    BARD = "Bard"
    BERSERKER = "Berserker"
    MONK = "Monk"

class RPGRole(str, Enum):
    TANK = "Tank"
    HEALER = "Healer"
    MELEE_DPS = "Melee DPS"
    RANGED_DPS = "Ranged DPS"
    MAGIC_DPS = "Magic DPS"
    SUPPORT = "Support"
    CRAFTSMAN = "Craftsman"

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
    sprite_name: str = "Klaus_Mueller"  # Character walk sprite sheet
    
    # MMORPG Character System Extensions
    rpg_class: str = "Warrior"
    role: str = "Melee DPS"
    level: int = 1
    hp: int = 100
    max_hp: int = 100
    mana: int = 50
    max_mana: int = 50
    gold: int = 50
    equipment: Dict[str, str] = Field(default_factory=lambda: {
        "weapon": "Iron Shortsword",
        "armor": "Leather Tunic",
        "accessory": "Traveler Amulet"
    })
    party_id: Optional[str] = None
    title: str = "Adventurer"
    dungeon_clears: int = 0
    monsters_slain: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
