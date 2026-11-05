from typing import List, Dict, Any, Optional
from app.agents.memory import MemoryStream, MemoryItem
from app.ai import get_ai_provider
from app.config import settings

class ReflectionEngine:
    @staticmethod
    def should_reflect(memory_stream: MemoryStream, current_sim_hour: int) -> bool:
        """Determines if the cumulative importance threshold is met or evening reflection has arrived."""
        if memory_stream.cumulative_importance_since_reflection >= settings.REFLECTION_THRESHOLD:
            return True
        if current_sim_hour == 21 and len(memory_stream.memories) >= 5:
            return True
        return False

    @staticmethod
    async def perform_reflection(
        npc_data: Dict[str, Any],
        memory_stream: MemoryStream,
        current_sim_minute: int
    ) -> List[MemoryItem]:
        """Synthesize high-level reflections and update beliefs."""
        recent_mems = memory_stream.get_recent(15)
        if not recent_mems:
            return []

        ai = get_ai_provider()
        reflection_output = await ai.generate_reflection(
            npc_data=npc_data,
            memories=[m.to_dict() for m in recent_mems]
        )

        formed_reflections: List[MemoryItem] = []
        for insight in reflection_output.insights:
            # Store insight as high-importance reflection memory
            mem = memory_stream.add_memory(
                content=f"[Reflection] {insight}",
                sim_timestamp=current_sim_minute,
                memory_type="reflection",
                importance=8.5
            )
            formed_reflections.append(mem)

        # Update beliefs in npc_data if present
        if "beliefs" in npc_data and reflection_output.new_beliefs:
            for belief in reflection_output.new_beliefs:
                if belief not in npc_data["beliefs"]:
                    npc_data["beliefs"].append(belief)

        # Reset accumulator
        memory_stream.cumulative_importance_since_reflection = 0.0
        return formed_reflections
