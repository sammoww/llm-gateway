import time
import httpx
from typing import Dict, Any, List
from app.api.schemas import ChatCompletionRequest, ProviderResult
from app.providers.base import BaseLLMProvider

class GroqProvider(BaseLLMProvider):
    """Adapter for Groq OpenAI-compatible Cloud API."""

    def __init__(self, api_key: str, default_model: str = "llama-3.1-8b-instant"):
        super().__init__(api_key, default_model)
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    async def complete(self, request: ChatCompletionRequest) -> ProviderResult:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

        # Groq uses standard Llama/Mixtral model names
        model = self.default_model if (not request.model or request.model == "auto" or "gemini" in request.model) else request.model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload: Dict[str, Any] = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature if request.temperature is not None else 0.7
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        start_time = time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.endpoint, headers=headers, json=payload)
            latency_ms = (time.time() - start_time) * 1000

            response.raise_for_status()
            data = response.json()

        try:
            choice = data["choices"][0]
            text = choice["message"]["content"]
        except (KeyError, IndexError) as err:
            raise ValueError(f"Unexpected response structure from Groq: {data}") from err

        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        return ProviderResult(
            content=text,
            provider_name="groq",
            model_name=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=round(latency_ms, 2),
            fallback_triggered=True
        )
