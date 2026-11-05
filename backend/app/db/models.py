from sqlalchemy import Column, Integer, Float, String, Text, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class NPCModel(Base):
    __tablename__ = "npcs"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    occupation = Column(String, nullable=False)
    
    # Personality (Big Five & Traits)
    personality = Column(JSON, nullable=False, default=dict)
    background = Column(Text, nullable=False)
    interests = Column(JSON, nullable=False, default=list)
    skills = Column(JSON, nullable=False, default=list)
    beliefs = Column(JSON, nullable=False, default=list)
    personal_values = Column(JSON, nullable=False, default=list)
    goals = Column(JSON, nullable=False, default=list)
    
    # Physical & Simulation State
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    current_location = Column(String, default="Residential District")
    current_activity = Column(String, default="Resting")
    emotion = Column(String, default="Relaxed")
    needs = Column(JSON, nullable=False, default=dict)
    wealth = Column(Float, default=100.0)
    home_id = Column(String, nullable=False)
    workplace_id = Column(String, nullable=False)

    # Relationships to other tables
    memories = relationship("MemoryModel", back_populates="npc", cascade="all, delete-orphan")
    reflections = relationship("ReflectionModel", back_populates="npc", cascade="all, delete-orphan")
    plans = relationship("PlanModel", back_populates="npc", cascade="all, delete-orphan")

class MemoryModel(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True)
    npc_id = Column(String, ForeignKey("npcs.id"), nullable=False)
    memory_type = Column(String, nullable=False, default="short_term")  # short_term, long_term, observation, conversation
    content = Column(Text, nullable=False)
    importance = Column(Float, nullable=False, default=5.0)  # 1 to 10
    sim_timestamp = Column(Integer, nullable=False)  # simulation minute
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(JSON, nullable=True)  # List of floats for semantic search
    retrieved_count = Column(Integer, default=0)
    last_accessed = Column(Integer, default=0)

    npc = relationship("NPCModel", back_populates="memories")

class ReflectionModel(Base):
    __tablename__ = "reflections"

    id = Column(String, primary_key=True)
    npc_id = Column(String, ForeignKey("npcs.id"), nullable=False)
    insight = Column(Text, nullable=False)
    supporting_memory_ids = Column(JSON, nullable=False, default=list)
    importance = Column(Float, default=7.0)
    sim_timestamp = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    npc = relationship("NPCModel", back_populates="reflections")

class RelationshipModel(Base):
    __tablename__ = "relationships"

    id = Column(String, primary_key=True)
    source_npc_id = Column(String, nullable=False, index=True)
    target_npc_id = Column(String, nullable=False, index=True)
    familiarity = Column(Float, default=0.0)  # 0 to 100
    trust = Column(Float, default=50.0)       # 0 to 100
    affinity = Column(Float, default=50.0)    # 0 to 100 (like/dislike)
    respect = Column(Float, default=50.0)     # 0 to 100
    conflict = Column(Float, default=0.0)     # 0 to 100
    shared_experiences_count = Column(Integer, default=0)
    relationship_type = Column(String, default="Acquaintance")  # Friend, Rival, Colleague, Family, etc.
    last_interaction = Column(Integer, default=0)

class PlanModel(Base):
    __tablename__ = "plans"

    id = Column(String, primary_key=True)
    npc_id = Column(String, ForeignKey("npcs.id"), nullable=False)
    sim_day = Column(Integer, nullable=False)
    schedule = Column(JSON, nullable=False, default=list)  # list of plan items: {start_hour, end_hour, activity, location, description}
    current_step_idx = Column(Integer, default=0)
    status = Column(String, default="active")  # active, completed, modified

    npc = relationship("NPCModel", back_populates="plans")

class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    participants = Column(JSON, nullable=False)  # list of npc_ids
    location_id = Column(String, nullable=False)
    sim_timestamp = Column(Integer, nullable=False)
    topic = Column(String, default="General")
    summary = Column(Text, nullable=True)

    messages = relationship("ConversationMessageModel", back_populates="conversation", cascade="all, delete-orphan")

class ConversationMessageModel(Base):
    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    speaker_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    turn_index = Column(Integer, nullable=False)
    sim_timestamp = Column(Integer, nullable=False)

    conversation = relationship("ConversationModel", back_populates="messages")

class WorldEventModel(Base):
    __tablename__ = "world_events"

    id = Column(String, primary_key=True)
    event_type = Column(String, nullable=False)  # social, economic, weather, community, emergent
    description = Column(Text, nullable=False)
    location_id = Column(String, nullable=False)
    initiator_id = Column(String, nullable=True)
    participants = Column(JSON, nullable=False, default=list)
    sim_timestamp = Column(Integer, nullable=False)
    significance = Column(Float, default=5.0)

class SimulationStateModel(Base):
    __tablename__ = "simulation_states"

    id = Column(Integer, primary_key=True, default=1)
    tick = Column(Integer, default=0)
    sim_minute = Column(Integer, default=0)
    sim_hour = Column(Integer, default=7)
    sim_day = Column(Integer, default=1)
    weather = Column(String, default="Sunny")
    is_running = Column(Boolean, default=True)
    speed = Column(Float, default=1.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

