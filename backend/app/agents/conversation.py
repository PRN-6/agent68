import uuid
from typing import List, Dict, Any, Optional
from app.ai import get_ai_provider
from app.core.events import event_bus

class ConversationSession:
    def __init__(
        self,
        npc_a: Any,
        npc_b: Any,
        location_id: str,
        sim_minute: int,
        topic: str = "Daily town life"
    ):
        self.id: str = str(uuid.uuid4())
        self.npc_a = npc_a
        self.npc_b = npc_b
        self.location_id = location_id
        self.start_sim_minute = sim_minute
        self.topic = topic
        self.messages: List[Dict[str, str]] = []
        self.is_completed: bool = False
        self.total_sentiment: float = 0.0

    async def execute_dialogue(self, max_turns: int = 4):
        ai = get_ai_provider()
        
        current_speaker = self.npc_a
        current_listener = self.npc_b
        
        for turn_idx in range(max_turns):
            rel = current_speaker.relationships.get_or_create(current_listener.id).to_dict()
            
            output = await ai.generate_dialogue_turn(
                speaker_data=current_speaker.get_profile_dict(),
                listener_data=current_listener.get_profile_dict(),
                conversation_history=self.messages,
                topic=self.topic,
                relationship_data=rel
            )
            
            self.messages.append({
                "speaker_id": current_speaker.id,
                "speaker_name": current_speaker.name,
                "message": output.utterance,
                "thought": output.thought
            })
            
            self.total_sentiment += output.sentiment

            # Broadcast conversation turn as an epistemic world event for bystanders
            event_bus.publish_event(
                event_type="dialogue",
                description=f"{current_speaker.name} said to {current_listener.name}: \"{output.utterance}\"",
                location_id=self.location_id,
                sim_timestamp=self.start_sim_minute + turn_idx,
                initiator_id=current_speaker.id,
                participants=[current_speaker.id, current_listener.id],
                significance=4.0
            )

            if output.end_conversation:
                break
                
            # Swap speaker and listener
            current_speaker, current_listener = current_listener, current_speaker

        self.is_completed = True
        avg_sentiment = self.total_sentiment / max(1, len(self.messages))
        
        # Form memories for both participants
        dialogue_summary = f"Had a conversation with {self.npc_b.name} about {self.topic} at {self.location_id}."
        self.npc_a.add_memory(
            content=dialogue_summary,
            sim_minute=self.start_sim_minute,
            memory_type="conversation",
            importance=5.5
        )
        self.npc_a.relationships.record_interaction(
            target_npc_id=self.npc_b.id,
            sentiment=avg_sentiment,
            topic=self.topic,
            sim_minute=self.start_sim_minute
        )
        self.npc_a.needs.satisfy("social", 25.0)

        dialogue_summary_b = f"Had a conversation with {self.npc_a.name} about {self.topic} at {self.location_id}."
        self.npc_b.add_memory(
            content=dialogue_summary_b,
            sim_minute=self.start_sim_minute,
            memory_type="conversation",
            importance=5.5
        )
        self.npc_b.relationships.record_interaction(
            target_npc_id=self.npc_a.id,
            sentiment=avg_sentiment,
            topic=self.topic,
            sim_minute=self.start_sim_minute
        )
        self.npc_b.needs.satisfy("social", 25.0)

        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "participants": [self.npc_a.id, self.npc_b.id],
            "participant_names": [self.npc_a.name, self.npc_b.name],
            "location_id": self.location_id,
            "topic": self.topic,
            "messages": self.messages,
            "is_completed": self.is_completed
        }
