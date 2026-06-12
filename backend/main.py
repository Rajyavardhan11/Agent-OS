"""FastAPI entrypoint for Agent OS."""

from __future__ import annotations

import logging

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FRONTEND_ORIGIN, OLLAMA_BASE_URL
from routes import memory, tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-os")

app = FastAPI(title="Agent OS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(memory.router)


@app.on_event("startup")
async def check_ollama() -> None:
    """Warn if Ollama is unavailable without blocking the app."""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            logger.info("Ollama is available")
    except Exception:
        logger.warning("Ollama is not available. Agents will return clear fallback output.")


@app.get("/")
async def root() -> dict[str, object]:
    """Health endpoint."""
    return {"status": "Agent OS running", "agents": 6}

