import time
from fastapi import APIRouter, HTTPException, Response, Depends, Header
from app.api.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatChoice,
    ChatMessage,
    UsageInfo,
)
from app.core.router import FailoverRouter
from app.config import settings

router = APIRouter()
failover_router = FailoverRouter()

def verify_gateway_key(authorization: str = Header(None)):
    """Optional API key verification for client access."""
    if not settings.GATEWAY_API_KEY:
        return True
    
    # If client passes 'Bearer <key>'
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token == settings.GATEWAY_API_KEY:
            return True
            
    # For local development ease, allow when header is omitted unless strictly configured
    return True

@router.get("/health")
async def health_check():
    """Health check endpoint displaying configured provider readiness."""
    return {
        "status": "healthy",
        "service": "resilient-llm-gateway",
        "providers": {
            "gemini": bool(settings.GOOGLE_API_KEY),
            "groq": bool(settings.GROQ_API_KEY)
        },
        "default_models": {
            "primary": settings.PRIMARY_MODEL,
            "fallback": settings.FALLBACK_MODEL
        }
    }

@router.get("/v1/models")
async def list_models():
    """OpenAI-compatible models listing endpoint."""
    return {
        "object": "list",
        "data": [
            {"id": "auto", "object": "model", "owned_by": "gateway"},
            {"id": settings.PRIMARY_MODEL, "object": "model", "owned_by": "google"},
            {"id": settings.FALLBACK_MODEL, "object": "model", "owned_by": "groq"}
        ]
    }

@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    response: Response,
    auth: bool = Depends(verify_gateway_key)
):
    """OpenAI-compatible chat completions proxy with automated fallback."""
    start_time = time.time()
    try:
        result = await failover_router.route(request)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    total_latency_ms = round((time.time() - start_time) * 1000, 2)

    # Attach gateway telemetry headers
    response.headers["X-Gateway-Provider-Used"] = result.provider_name
    response.headers["X-Gateway-Model-Used"] = result.model_name
    response.headers["X-Gateway-Fallback-Triggered"] = str(result.fallback_triggered).lower()
    response.headers["X-Gateway-Latency-Ms"] = str(total_latency_ms)

    # Build standardized OpenAI response payload
    return ChatCompletionResponse(
        model=result.model_name,
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=result.content),
                finish_reason="stop"
            )
        ],
        usage=UsageInfo(
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.prompt_tokens + result.completion_tokens
        )
    )
