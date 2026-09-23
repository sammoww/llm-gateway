from abc import ABC, abstractmethod
from app.api.schemas import ChatCompletionRequest, ProviderResult

class BaseLLMProvider(ABC):
    """Abstract interface that all upstream LLM adapters must implement."""

    def __init__(self, api_key: str, default_model: str):
        self.api_key = api_key
        self.default_model = default_model

    @abstractmethod
    async def complete(self, request: ChatCompletionRequest) -> ProviderResult:
        """Executes a chat completion call against the provider API."""
        pass
