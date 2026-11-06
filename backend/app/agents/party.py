import random
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from app.core.events import event_bus
from app.world.locations import get_location

logger = logging.getLogger(__name__)

class PartyStatus(str, Enum):
    IDLE = "IDLE"
    GATHERING_AT_GUILD = "GATHERING_AT_GUILD"
    PREPARING_AT_TAVERN = "PREPARING_AT_TAVERN"
    MARCHING_TO_DUNGEON = "MARCHING_TO_DUNGEON"
    EXPLORING_CRYPT = "EXPLORING_CRYPT"
    EXPLORING_CATACOMBS = "EXPLORING_CATACOMBS"
    FIGHTING_BOSS = "FIGHTING_BOSS"
    RETURNING_VICTORIOUS = "RETURNING_VICTORIOUS"
    CELEBRATING_AT_TAVERN = "CELEBRATING_AT_TAVERN"

class DungeonEncounter(BaseModel):
    name: str
    monster_type: str
    hp: int
    max_hp: int
    attack: int
    loot_gold: int
    rare_drop: Optional[str] = None

class AdventuringParty:
    def __init__(
        self,
        party_id: str,
        name: str,
        leader_id: str,
        member_ids: List[str],
        banner_color: str = "#3B82F6"
    ):
        self.party_id = party_id
        self.name = name
        self.leader_id = leader_id
        self.member_ids = member_ids
        self.banner_color = banner_color
        self.status: PartyStatus = PartyStatus.IDLE
        self.current_dungeon_room: Optional[str] = None
        self.expedition_step: int = 0
        self.combat_logs: List[str] = []
        self.total_loot_gold: int = 0
        self.dungeon_clears: int = 0
        self.target_room: Optional[str] = None
        self.state_timer: int = random.randint(15, 30)
        self.current_monster: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "party_id": self.party_id,
            "name": self.name,
            "leader_id": self.leader_id,
            "member_ids": self.member_ids,
            "banner_color": self.banner_color,
            "status": self.status.value,
            "current_dungeon_room": self.current_dungeon_room,
            "dungeon_clears": self.dungeon_clears,
            "total_loot_gold": self.total_loot_gold,
            "latest_log": self.combat_logs[-1] if self.combat_logs else "Resting in Sunhaven.",
            "current_monster": self.current_monster
        }

    async def tick_expedition(
        self,
        npcs: Dict[str, Any],
        sim_minute: int
    ):
        """Simulate party progression, formation movement, encounters, and loot."""
        self.state_timer -= 1
        if self.state_timer > 0:
            return

        leader = npcs.get(self.leader_id)
        if not leader:
            return

        # -------------------------------------------------------------
        # STATE MACHINE: From Guild Hall -> Dungeon Boss -> Tavern!
        # -------------------------------------------------------------
        if self.status == PartyStatus.IDLE:
            # Trigger expedition call at the Adventurer's Guild
            self.status = PartyStatus.GATHERING_AT_GUILD
            self.state_timer = 15
            for mid in self.member_ids:
                m = npcs.get(mid)
                if m:
                    m.current_activity = f"Assembling with {self.name} at Guild Hall"
                    guild_loc = get_location("guild_hall")
                    if guild_loc:
                        m.set_destination(guild_loc.walk_x + random.uniform(-2, 2), guild_loc.walk_y + random.uniform(-2, 2))
                    m.add_memory(
                        f"Guild Master called {self.name} to assemble at the Adventurer's Guild for a dungeon contract.",
                        sim_minute, importance=6.0
                    )
            event_bus.publish_event(
                event_type="party_gathering",
                description=f"⚔️ {self.name} received a new dungeon quest contract and is gathering at the Adventurer's Guild!",
                location_id="guild_hall",
                sim_timestamp=sim_minute,
                significance=6.0,
                present_npc_ids=self.member_ids
            )

        elif self.status == PartyStatus.GATHERING_AT_GUILD:
            # Move to tavern for food/ale buffs
            self.status = PartyStatus.PREPARING_AT_TAVERN
            self.state_timer = 18
            for mid in self.member_ids:
                m = npcs.get(mid)
                if m:
                    m.current_activity = "Toasting flagons of ale at Dragon's Flagon"
                    t_loc = get_location("tavern")
                    if t_loc:
                        m.set_destination(t_loc.walk_x + random.uniform(-2, 2), t_loc.walk_y + random.uniform(-2, 2))
                    m.needs.satisfy("fun", 30.0)
                    m.needs.satisfy("hunger", 30.0)
            event_bus.publish_event(
                event_type="party_buff",
                description=f"🍺 {self.name} is drinking dragon-draughts at the tavern, steeling their nerves for the crypts!",
                location_id="tavern",
                sim_timestamp=sim_minute,
                significance=5.0,
                present_npc_ids=self.member_ids
            )

        elif self.status == PartyStatus.PREPARING_AT_TAVERN:
            # March over Stone Bridge through Whispering Forest to Dungeon Entrance
            self.status = PartyStatus.MARCHING_TO_DUNGEON
            self.state_timer = 25
            d_gate = get_location("dungeon_entrance")
            for idx, mid in self.member_ids:
                m = npcs.get(mid)
                if m and d_gate:
                    m.current_activity = f"Marching with {self.name} to the Shadow Crypts"
                    # Slight offset so party marches together in formation
                    m.set_destination(d_gate.walk_x + (idx * 0.5), d_gate.walk_y + (idx * 0.3))
            event_bus.publish_event(
                event_type="dungeon_march",
                description=f"🛡️ {self.name} crossed the Grand Stone Bridge into Whispering Forest, heading toward the Dungeon Skull Gate!",
                location_id="stone_bridge",
                sim_timestamp=sim_minute,
                significance=7.0,
                present_npc_ids=self.member_ids
            )

        elif self.status == PartyStatus.MARCHING_TO_DUNGEON:
            # Enter Room 1: Crypt of the Undead
            self.status = PartyStatus.EXPLORING_CRYPT
            self.current_dungeon_room = "dungeon_crypt"
            self.state_timer = 20
            crypt = get_location("dungeon_crypt")
            for idx, mid in self.member_ids:
                m = npcs.get(mid)
                if m and crypt:
                    m.current_location = "dungeon_crypt"
                    m.current_activity = "Fighting Skeleton Warriors in Crypt of the Undead"
                    m.set_destination(crypt.walk_x + (idx * 0.8), crypt.walk_y + (idx * 0.5))
                    # Take some battle damage, cast spells
                    m.hp = max(20, m.hp - random.randint(10, 25))
                    m.mana = max(10, m.mana - random.randint(15, 30))
                    m.monsters_slain += 1

            self.current_monster = {"name": "Bone Crusher Skeleton Champion", "hp": 0, "max_hp": 250, "status": "Defeated"}
            log_entry = f"{self.name} breached Floor 1: Defeated the Skeleton Champion! Cleric cast Holy Radiance, saving the frontline!"
            self.combat_logs.append(log_entry)
            event_bus.publish_event(
                event_type="dungeon_combat",
                description=f"⚔️ [Floor 1 - Crypt] {log_entry}",
                location_id="dungeon_crypt",
                sim_timestamp=sim_minute,
                significance=7.5,
                present_npc_ids=self.member_ids
            )

        elif self.status == PartyStatus.EXPLORING_CRYPT:
            # Enter Room 2: Catacombs & Treasure Vault
            self.status = PartyStatus.EXPLORING_CATACOMBS
            self.current_dungeon_room = "dungeon_catacombs"
            self.state_timer = 22
            catacombs = get_location("dungeon_catacombs")
            loot_found = random.randint(150, 320)
            self.total_loot_gold += loot_found

            for idx, mid in self.member_ids:
                m = npcs.get(mid)
                if m and catacombs:
                    m.current_location = "dungeon_catacombs"
                    m.current_activity = "Disarming traps & looting gilded chests in Catacombs"
                    m.set_destination(catacombs.walk_x + (idx * 0.7), catacombs.walk_y + (idx * 0.4))
                    m.wealth += loot_found // len(self.member_ids)
                    m.add_memory(
                        f"Looted ancient gilded vault in Catacombs with {self.name}, earning {loot_found // len(self.member_ids)} gold coins!",
                        sim_minute, importance=7.0
                    )

            self.current_monster = {"name": "Shadow Vault Wraith", "hp": 0, "max_hp": 300, "status": "Banished"}
            log_entry = f"{self.name} unlocked the Gilded Vault: +{loot_found} Gold Coins & Ancient Gems retrieved!"
            self.combat_logs.append(log_entry)
            event_bus.publish_event(
                event_type="dungeon_loot",
                description=f"💰 [Floor 2 - Vault] {log_entry}",
                location_id="dungeon_catacombs",
                sim_timestamp=sim_minute,
                significance=8.0,
                present_npc_ids=self.member_ids
            )

        elif self.status == PartyStatus.EXPLORING_CATACOMBS:
            # Enter Room 3: The Abyssal Boss Chamber!
            self.status = PartyStatus.FIGHTING_BOSS
            self.current_dungeon_room = "dungeon_boss_chamber"
            self.state_timer = 26
            boss_chamber = get_location("dungeon_boss_chamber")
            boss_name = random.choice(["The Abyssal Void Dragon", "Lord Malakor the Death Knight", "Infernal Shadow Overlord"])

            for idx, mid in self.member_ids:
                m = npcs.get(mid)
                if m and boss_chamber:
                    m.current_location = "dungeon_boss_chamber"
                    m.current_activity = f"EPIC BOSS BATTLE against {boss_name}!"
                    m.set_destination(boss_chamber.walk_x + (idx * 0.8), boss_chamber.walk_y + (idx * 0.5))
                    # Heavy boss damage & intense magic
                    m.hp = max(15, m.hp - random.randint(20, 45))
                    m.mana = max(5, m.mana - random.randint(25, 45))
                    m.monsters_slain += 2
                    m.dungeon_clears += 1
                    # Level up check
                    if random.random() < 0.35:
                        m.level += 1
                        m.max_hp += 15
                        m.hp = m.max_hp
                        m.max_mana += 10
                        m.mana = m.max_mana
                        m.add_memory(f"LEVELED UP to Level {m.level} after defeating {boss_name}!", sim_minute, importance=9.0)

            self.dungeon_clears += 1
            boss_gold = random.randint(400, 750)
            self.total_loot_gold += boss_gold
            self.current_monster = {"name": boss_name, "hp": 0, "max_hp": 800, "status": "SLAIN"}
            log_entry = f"VICTORY! {self.name} vanquished {boss_name}! Claimed {boss_gold} Gold & Abyssal Relic!"
            self.combat_logs.append(log_entry)
            event_bus.publish_event(
                event_type="boss_slain",
                description=f"🏆 [BOSS CLEARED] {log_entry}",
                location_id="dungeon_boss_chamber",
                sim_timestamp=sim_minute,
                significance=10.0,
                present_npc_ids=self.member_ids
            )

        elif self.status == PartyStatus.FIGHTING_BOSS:
            # Victorious March back to Sunhaven
            self.status = PartyStatus.RETURNING_VICTORIOUS
            self.current_dungeon_room = None
            self.state_timer = 25
            tavern_loc = get_location("tavern")
            for idx, mid in self.member_ids:
                m = npcs.get(mid)
                if m and tavern_loc:
                    m.current_activity = f"Marching back triumphant with {self.name}"
                    m.set_destination(tavern_loc.walk_x + (idx * 0.5), tavern_loc.walk_y + (idx * 0.4))
            event_bus.publish_event(
                event_type="party_return",
                description=f"🎉 {self.name} emerged triumphant from the dungeon, crossing the bridge with heavy gold sacks!",
                location_id="stone_bridge",
                sim_timestamp=sim_minute,
                significance=8.0,
                present_npc_ids=self.member_ids
            )

        elif self.status == PartyStatus.RETURNING_VICTORIOUS:
            # Celebrating at Dragon's Flagon Tavern!
            self.status = PartyStatus.CELEBRATING_AT_TAVERN
            self.state_timer = 35
            for mid in self.member_ids:
                m = npcs.get(mid)
                if m:
                    m.current_location = "tavern"
                    m.current_activity = "Singing victory songs & drinking ale at Dragon's Flagon"
                    m.needs.satisfy("fun", 50.0)
                    m.needs.satisfy("social", 50.0)
                    m.emotions.current_intensity = 0.95
                    m.add_memory(
                        f"Celebrated our dungeon conquest at the Dragon's Flagon Tavern with {self.name}! The town cheered our bravery.",
                        sim_minute, importance=8.0
                    )
            event_bus.publish_event(
                event_type="tavern_celebration",
                description=f"🍻 Dragon's Flagon erupted in cheers as {self.name} bought a round of victory ale for the entire tavern!",
                location_id="tavern",
                sim_timestamp=sim_minute,
                significance=7.5,
                present_npc_ids=self.member_ids
            )

        elif self.status == PartyStatus.CELEBRATING_AT_TAVERN:
            # Enter Rest / Idle cycle
            self.status = PartyStatus.IDLE
            self.state_timer = random.randint(40, 80)
            for mid in self.member_ids:
                m = npcs.get(mid)
                if m:
                    m.current_activity = "Resting in Sunhaven"


class PartyManager:
    def __init__(self):
        self.parties: Dict[str, AdventuringParty] = {}
        self._initialize_default_parties()

    def _initialize_default_parties(self):
        # 1. The Silver Vanguard (Balanced Classic Raid Party)
        self.parties["party_silver_vanguard"] = AdventuringParty(
            party_id="party_silver_vanguard",
            name="The Silver Vanguard",
            leader_id="npc_arthur_vance",
            member_ids=[
                "npc_arthur_vance",   # Paladin / Tank
                "npc_clara_bennett",   # High Cleric / Healer
                "npc_sarah_jenkins",   # Arcane Mage / Magic DPS
                "npc_lucas_gray",      # Berserker / Melee DPS
                "npc_sam_moore"        # Squire / Paladin
            ],
            banner_color="#3B82F6"
        )
        # 2. The Shadow Stalkers (Stealth & Burst Party)
        self.parties["party_shadow_stalkers"] = AdventuringParty(
            party_id="party_shadow_stalkers",
            name="The Shadow Stalkers",
            leader_id="npc_elena_rostova",
            member_ids=[
                "npc_elena_rostova",   # Shadow Rogue / Melee DPS
                "npc_carlos_gomez",    # Forest Ranger / Ranged DPS
                "npc_mei_lin",         # Wind Monk / Striker
                "npc_marcus_thorne"    # Alchemist / Support
            ],
            banner_color="#10B981"
        )
        # 3. The Crimson Dawn (Heavy Boss Slaying Raid)
        self.parties["party_crimson_dawn"] = AdventuringParty(
            party_id="party_crimson_dawn",
            name="The Crimson Dawn",
            leader_id="npc_tamara_taylor",
            member_ids=[
                "npc_tamara_taylor",   # Dragon Slayer Berserker
                "npc_wolfgang_schulz", # Grand Pyromancer
                "npc_carmen_ortiz",    # Celestial Priestess
                "npc_eddy_lin",        # Scout / Trapper
                "npc_jennifer_moore"   # Bard / Enchanter
            ],
            banner_color="#EF4444"
        )

    def get_party(self, party_id: str) -> Optional[AdventuringParty]:
        return self.parties.get(party_id)

    def get_all_parties(self) -> List[AdventuringParty]:
        return list(self.parties.values())

    async def update_tick(self, npcs: Dict[str, Any], sim_minute: int):
        for party in self.parties.values():
            await party.tick_expedition(npcs, sim_minute)

party_manager = PartyManager()
