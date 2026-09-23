# Resilient LLM Gateway

A high-performance, OpenAI-compatible LLM Gateway and reverse proxy service designed for reliability, automated provider failover, and cost optimization.

## Key Features
- **OpenAI-Compatible Endpoint:** Accepts `/v1/chat/completions` so any OpenAI client, LangChain, or agent framework can connect seamlessly.
- **Smart Failover & Resilience:** Routes requests primarily to Google Gemini, with automatic zero-delay fallback to Groq on timeouts, 429 rate limits, or 5xx server errors.
- **Response Caching:** In-memory / fast caching for duplicate queries, serving responses in <10ms at $0 API cost.
- **Observability:** Tracks latency, token counts (prompt vs completion), and provider status per request.

## Tech Stack
- **Framework:** FastAPI / Uvicorn
- **HTTP Engine:** HTTPX (async)
- **Validation:** Pydantic v2
- **Providers:** Google Gemini (`gemini-3.5-flash`), Groq (`llama3-8b-8192`)
