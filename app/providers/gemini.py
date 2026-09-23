import time
import httpx
from typing import Dict, Any, List
from app.api.schemas import ChatCompletionRequest, ProviderResult
from app.providers.base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    """Adapter for Google Gemini REST API."""

    def __init__(self, api_key: str, default_model: str = "gemini-3.5-flash"):
        super().__init__(api_key, default_model)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def complete(self, request: ChatCompletionRequest) -> ProviderResult:
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not configured.")

        model = self.default_model if (not request.model or request.model == "auto") else request.model
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"

        # Convert OpenAI messages to Gemini contents structure
        contents: List[Dict[str, Any]] = []
        system_instruction_text = None

        for msg in request.messages:
            if msg.role == "system":
                system_instruction_text = msg.content
            else:
                role = "model" if msg.role == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })

        payload: Dict[str, Any] = {"contents": contents}

        if system_instruction_text:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction_text}]
            }

        generation_config: Dict[str, Any] = {}
        if request.temperature is not None:
            generation_config["temperature"] = request.temperature
        if request.max_tokens is not None:
            generation_config["maxOutputTokens"] = request.max_tokens

        if generation_config:
            payload["generationConfig"] = generation_config

        start_time = time.time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            latency_ms = (time.time() - start_time) * 1000

            response.raise_for_status()
            data = response.json()

        # Parse Gemini response structure
        try:
            candidate = data["candidates"][0]
            text = candidate["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as err:
            raise ValueError(f"Unexpected response structure from Gemini: {data}") from err

        usage_meta = data.get("usageMetadata", {})
        prompt_tokens = usage_meta.get("promptTokenCount", 0)
        completion_tokens = usage_meta.get("candidatesTokenCount", 0)

        return ProviderResult(
            content=text,
            provider_name="gemini",
            model_name=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=round(latency_ms, 2),
            fallback_triggered=False
        )
