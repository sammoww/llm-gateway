import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Upstream Provider Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Server Configuration
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))
    GATEWAY_API_KEY: str = os.getenv("GATEWAY_API_KEY", "gw-secret-key-12345")

    # Routing Defaults
    PRIMARY_MODEL: str = "gemini-3.5-flash"
    FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    DEFAULT_TIMEOUT_SECONDS: float = 8.0

settings = Settings()
