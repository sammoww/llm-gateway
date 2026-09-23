import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("llm_gateway")

def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="Resilient LLM Gateway",
        description="High-availability OpenAI-compatible LLM Gateway with automated provider failover and telemetry.",
        version="0.1.0"
    )

    # Enable CORS for web clients / dashboards
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routes
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup():
        logger.info("=" * 60)
        logger.info("Resilient LLM Gateway booting up...")
        logger.info(f"Host: {settings.GATEWAY_HOST} | Port: {settings.GATEWAY_PORT}")
        logger.info(f"Primary Provider : Google Gemini ({settings.PRIMARY_MODEL})")
        logger.info(f"Fallback Provider: Groq ({settings.FALLBACK_MODEL})")
        logger.info(f"Google Key Configured: {'Yes' if settings.GOOGLE_API_KEY else 'NO'}")
        logger.info(f"Groq Key Configured  : {'Yes' if settings.GROQ_API_KEY else 'NO'}")
        logger.info("=" * 60)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.GATEWAY_HOST, port=settings.GATEWAY_PORT, reload=True)
