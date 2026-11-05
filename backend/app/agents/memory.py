import uuid
import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.ai.embeddings import embedding_provider
from app.config import settings

class MemoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    npc_id: str
    memory_type: str = "short_term"  # short_term, long_term, observation, conversation, reflection
    content: str
    importance: float = 5.0          # 1.0 to 10.0
    sim_timestamp: int               # Simulation minute when formed
    real_timestamp: datetime = Field(default_factory=datetime.utcnow)
    embedding: List[float] = Field(default_factory=list)
    retrieved_count: int = 0
    last_accessed_minute: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "npc_id": self.npc_id,
            "memory_type": self.memory_type,
            "content": self.content,
            "importance": self.importance,
            "sim_timestamp": self.sim_timestamp,
            "retrieved_count": self.retrieved_count,
            "last_accessed_minute": self.last_accessed_minute
        }

class MemoryStream:
    def __init__(self, npc_id: str):
        self.npc_id = npc_id
        self.memories: List[MemoryItem] = []
        self.cumulative_importance_since_reflection: float = 0.0

    def add_memory(
        self,
        content: str,
        sim_timestamp: int,
        memory_type: str = "short_term",
        importance: float = 5.0
    ) -> MemoryItem:
        """Form a new memory with embedded vector and importance score."""
        emb = embedding_provider.embed_text(content)
        
        # Long-term promotion if importance >= 8.0
        if importance >= 8.0 and memory_type == "short_term":
            memory_type = "long_term"
            
        mem = MemoryItem(
            npc_id=self.npc_id,
            memory_type=memory_type,
            content=content,
            importance=max(1.0, min(10.0, importance)),
            sim_timestamp=sim_timestamp,
            embedding=emb,
            last_accessed_minute=sim_timestamp
        )
        self.memories.append(mem)
        self.cumulative_importance_since_reflection += mem.importance
        return mem

    def retrieve(
        self,
        query: str,
        current_sim_minute: int,
        top_k: int = 5,
        alpha_recency: float = 1.0,
        alpha_importance: float = 1.0,
        alpha_relevance: float = 1.5
    ) -> List[MemoryItem]:
        """Stanford Generative Agents 3-factor retrieval formula:
        Score = alpha_recency * Recency + alpha_importance * Importance + alpha_relevance * Relevance
        """
        if not self.memories:
            return []

        query_emb = embedding_provider.embed_text(query)
        scored_memories = []

        for mem in self.memories:
            # 1. Recency: exponential decay over simulated hours
            hours_diff = max(0, (current_sim_minute - mem.sim_timestamp) / 60.0)
            recency_score = math.pow(settings.RECENCY_DECAY_RATE, hours_diff)

            # 2. Importance: scaled 0.1 to 1.0
            importance_score = mem.importance / 10.0

            # 3. Relevance: cosine similarity
            if mem.embedding and query_emb:
                relevance_score = max(0.0, embedding_provider.cosine_similarity(query_emb, mem.embedding))
            else:
                relevance_score = 0.5

            total_score = (
                alpha_recency * recency_score +
                alpha_importance * importance_score +
                alpha_relevance * relevance_score
            )

            scored_memories.append((total_score, mem))

        # Sort by total score descending
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_memories = [m for _, m in scored_memories[:top_k]]

        # Update access stats
        for m in top_memories:
            m.retrieved_count += 1
            m.last_accessed_minute = current_sim_minute

        return top_memories

    def get_recent(self, count: int = 10) -> List[MemoryItem]:
        return self.memories[-count:]

    def get_reflections(self) -> List[MemoryItem]:
        return [m for m in self.memories if m.memory_type == "reflection"]

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.memories]

