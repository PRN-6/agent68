import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Project Genesis - Autonomous AI Society"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./genesis.db"
    
    # Simulation Defaults
    DEFAULT_TICK_RATE_MS: int = 250  # 4 ticks per second by default
    MINUTES_PER_TICK: int = 1         # 1 tick = 1 simulated minute
    DEFAULT_SPEED_MULTIPLIER: float = 1.0
    
    # AI Reasoning Provider: "mock", "gemini", or "openai"
    AI_PROVIDER: str = "mock"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Memory and Reflection Parameters
    REFLECTION_THRESHOLD: float = 25.0  # Cumulative importance trigger
    MAX_RETRIEVAL_MEMORIES: int = 5
    RECENCY_DECAY_RATE: float = 0.995
    ALPHA_RECENCY: float = 1.0
    ALPHA_IMPORTANCE: float = 1.0
    ALPHA_RELEVANCE: float = 1.5

settings = Settings()
