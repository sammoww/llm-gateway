import logging
from typing import Tuple
from app.api.schemas import ChatCompletionRequest, ProviderResult
from app.providers.base import BaseLLMProvider
from app.providers.gemini import GeminiProvider
from app.providers.groq import GroqProvider
from app.config import settings

logger = logging.getLogger("llm_gateway.router")

class FailoverRouter:
    """Orchestrates requests between Primary and Fallback LLM providers."""

    def __init__(self):
        self.primary_provider = GeminiProvider(
            api_key=settings.GOOGLE_API_KEY,
            default_model=settings.PRIMARY_MODEL
        )
        self.fallback_provider = GroqProvider(
            api_key=settings.GROQ_API_KEY,
            default_model=settings.FALLBACK_MODEL
        )

    async def route(self, request: ChatCompletionRequest) -> ProviderResult:
        """Attempts primary provider first; automatically switches to fallback upon failure."""
        primary_name = self.primary_provider.__class__.__name__
        fallback_name = self.fallback_provider.__class__.__name__

        # 1. Try Primary Provider (Google Gemini)
        try:
            logger.info(f"Dispatching request to primary provider ({primary_name})...")
            result = await self.primary_provider.complete(request)
            result.fallback_triggered = False
            return result
        except Exception as primary_error:
            logger.warning(
                f"Primary provider {primary_name} failed: {primary_error}. "
                f"Triggering automated failover to {fallback_name}..."
            )

        # 2. Try Fallback Provider (Groq)
        try:
            result = await self.fallback_provider.complete(request)
            result.fallback_triggered = True
            logger.info(f"Fallback provider {fallback_name} successfully answered request.")
            return result
        except Exception as fallback_error:
            logger.error(f"Fallback provider {fallback_name} also failed: {fallback_error}.")
            raise RuntimeError(
                f"All providers exhausted. Primary failed with: {primary_error} | "
                f"Fallback failed with: {fallback_error}"
            )
