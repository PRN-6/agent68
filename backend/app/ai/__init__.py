from app.ai.provider import LLMProvider
from app.ai.mock_provider import DeterministicMockProvider
from app.ai.gemini_provider import GeminiProvider
from app.config import settings

_provider_instance = None

def get_ai_provider() -> LLMProvider:
    global _provider_instance
    if _provider_instance is None:
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            _provider_instance = GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
        else:
            _provider_instance = DeterministicMockProvider()
    return _provider_instance

def set_ai_provider(provider: LLMProvider):
    global _provider_instance
    _provider_instance = provider

