"""Writer agent."""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentOSState


class WriterAgent(BaseAgent):
    """Synthesize agent outputs into polished markdown."""

    name = "writer"
    system_prompt = (
        "You are a professional technical writer. Create clear, well-structured, "
        "engaging content."
    )

    async def run(self, state: AgentOSState) -> dict[str, Any]:
        logs = self.log_start(state)
        prompt = f"""
Task: {state["original_task"]}
Plan: {state.get("plan", "")}
Research: {state.get("research", "")}
Code: {state.get("code", "")}

Detect the best output format and synthesize all inputs into polished markdown.
"""
        draft = await self.ollama_call(prompt, self.system_prompt, temperature=0.55)
        if draft == "Ollama not available":
            draft = (
                f"# Result\n\nTask: {state['original_task']}\n\n"
                f"## Plan\n{state.get('plan', '')}\n\n"
                f"## Research\n{state.get('research', '')}\n\n"
                f"## Code\n{state.get('code', '')}"
            )
        self.shared_memory.store("task_memory", state["task_id"], draft, {"agent": self.name})
        return {"draft": draft, "agent_logs": self.log_done(logs, draft)}

