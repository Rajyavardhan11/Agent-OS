"""Planner agent."""

from __future__ import annotations

from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentOSState


class PlannerAgent(BaseAgent):
    """Break a task into actionable subtasks."""

    name = "planner"
    system_prompt = (
        "You are a strategic planner. Break down complex tasks into clear, "
        "actionable subtasks."
    )

    async def run(self, state: AgentOSState) -> dict[str, Any]:
        logs = self.log_start(state)
        prompt = f"""
Task: {state["original_task"]}
Memory context: {state.get("memory_context", "")}
Router decision: {state.get("router_decision", {})}

Create a numbered plan with 3-5 subtasks max. Each subtask must start with
a clear action verb and name a specific deliverable.
"""
        plan = await self.ollama_call(prompt, self.system_prompt, temperature=0.4)
        if plan == "Ollama not available":
            plan = (
                "1. Clarify the requested outcome and success criteria.\n"
                "2. Gather the relevant facts, constraints, and examples.\n"
                "3. Produce the requested deliverable in a polished format.\n"
                "4. Review the output for accuracy, completeness, and clarity."
            )
        self.shared_memory.store("task_memory", state["task_id"], plan, {"agent": self.name})
        return {"plan": plan, "agent_logs": self.log_done(logs, plan)}

