"""Memory manager agent."""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentOSState


class MemoryManagerAgent(BaseAgent):
    """Fetch relevant long-term context before routing."""

    name = "memory_manager"

    async def run(self, state: AgentOSState) -> dict[str, Any]:
        logs = self.log_start(state)
        memories = self.shared_memory.retrieve(
            "long_term_memory", state["original_task"], n_results=5
        )
        context = (
            "Relevant context from memory:\n" + "\n".join(f"- {item}" for item in memories)
            if memories
            else "No relevant memory found."
        )
        return {"memory_context": context, "agent_logs": self.log_done(logs, context)}

