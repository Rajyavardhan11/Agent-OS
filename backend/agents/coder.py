"""Coder agent."""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentOSState


class CoderAgent(BaseAgent):
    """Generate production-ready code for implementation tasks."""

    name = "coder"
    system_prompt = (
        "You are an expert software engineer. Write clean, well-commented, "
        "production-ready code."
    )

    async def run(self, state: AgentOSState) -> dict[str, Any]:
        logs = self.log_start(state)
        prompt = f"""
Task: {state["original_task"]}
Plan: {state.get("plan", "")}
Research: {state.get("research", "")}

Detect the best language from context, defaulting to Python. Write complete working code
with docstrings on every function, type hints, error handling, and a usage example.
Include a short explanation after the code.
"""
        code = await self.ollama_call(prompt, self.system_prompt, temperature=0.35)
        if code == "Ollama not available":
            code = (
                "```python\n"
                "def main() -> None:\n"
                "    \"\"\"Run the generated task placeholder safely.\"\"\"\n"
                "    print('Ollama is not available. Start Ollama to generate task-specific code.')\n\n"
                "if __name__ == '__main__':\n"
                "    main()\n"
                "```"
            )
        self.shared_memory.store("task_memory", state["task_id"], code, {"agent": self.name})
        return {"code": code, "agent_logs": self.log_done(logs, code)}

