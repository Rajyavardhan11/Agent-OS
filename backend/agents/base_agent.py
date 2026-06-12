"""Base behavior shared by all specialized agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import httpx

from config import OLLAMA_BASE_URL, OLLAMA_FALLBACK_MODEL, OLLAMA_MODEL
from graph.state import AgentOSState
from memory.shared_memory import SharedMemory


class BaseAgent(ABC):
    """Abstract base class for Agent OS agents."""

    name = "base"
    _resolved_model: str | None = None

    def __init__(self, shared_memory: SharedMemory) -> None:
        self.shared_memory = shared_memory

    async def _resolve_ollama_model(self, client: httpx.AsyncClient) -> str:
        """Choose an installed Ollama model, falling back to any local model."""
        if BaseAgent._resolved_model:
            return BaseAgent._resolved_model

        preferred_models = [
            OLLAMA_MODEL,
            OLLAMA_FALLBACK_MODEL,
            f"{OLLAMA_MODEL}:latest" if ":" not in OLLAMA_MODEL else OLLAMA_MODEL,
            f"{OLLAMA_FALLBACK_MODEL}:latest" if OLLAMA_FALLBACK_MODEL and ":" not in OLLAMA_FALLBACK_MODEL else OLLAMA_FALLBACK_MODEL,
        ]
        preferred_models = [model for model in preferred_models if model]

        try:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            installed_models = [
                str(model.get("name") or model.get("model"))
                for model in response.json().get("models", [])
                if model.get("name") or model.get("model")
            ]
        except Exception:
            installed_models = []

        for preferred in preferred_models:
            if preferred in installed_models:
                BaseAgent._resolved_model = preferred
                return preferred

        if installed_models:
            BaseAgent._resolved_model = installed_models[0]
            return installed_models[0]

        BaseAgent._resolved_model = OLLAMA_MODEL
        return OLLAMA_MODEL

    async def ollama_call(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """Call Ollama chat API and return text, with fallback model support."""
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                model = await self._resolve_ollama_model(client)
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "options": {"temperature": temperature},
                }
                response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
                if response.status_code == 404:
                    BaseAgent._resolved_model = None
                    model = await self._resolve_ollama_model(client)
                    payload["model"] = model
                    response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return str(data.get("message", {}).get("content", "")).strip()
        except httpx.HTTPStatusError as exc:
            return f"Ollama request failed: {exc.response.status_code} {exc.response.text[:160]}"
        except Exception as exc:
            return f"Ollama not available: {exc}"

    def log_start(self, state: AgentOSState) -> list[dict[str, Any]]:
        """Append a running log entry."""
        logs = list(state.get("agent_logs", []))
        logs.append(
            {
                "agent": self.name,
                "status": "running",
                "output": "",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return logs

    def log_done(self, logs: list[dict[str, Any]], output: str) -> list[dict[str, Any]]:
        """Mark this agent's latest log entry as complete."""
        updated = list(logs)
        for index in range(len(updated) - 1, -1, -1):
            if updated[index].get("agent") == self.name:
                updated[index] = {
                    **updated[index],
                    "status": "done",
                    "output": output[:200],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                break
        return updated

    def log_error(self, state: AgentOSState, error: Exception | str) -> list[str]:
        """Append a non-fatal error message."""
        return [*state.get("error_log", []), f"{self.name}: {error}"]

    @abstractmethod
    async def run(self, state: AgentOSState) -> dict[str, Any]:
        """Run an agent and return state updates."""
