# LLM Gateway Agent Context

This file contains the context and rules for AI agents working on the LLM Gateway project.

## Context
- **Project Goal:** Build a resilient, high-performance, OpenAI-compatible LLM Gateway with multi-provider routing (Gemini + Groq fallback), latency/token tracking, and caching.
- **Architecture:** FastAPI reverse-proxy implementing OpenAI `/v1/chat/completions` specification, intelligent failover on 429/5xx/timeout errors, and response caching.
- **Rules:** Follow canonical rules from `C:\Users\rajus\.agents\global-rules.md`. Update `worklog.md` after significant progress.
