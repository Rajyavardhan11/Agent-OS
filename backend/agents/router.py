"""Router agent that chooses the agent team and execution order."""

from __future__ import annotations

import json
import re
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentOSState


DEFAULT_DECISION: dict[str, Any] = {
    "task_type": "mixed",
    "complexity": "high",
    "agents_needed": ["planner", "researcher", "coder", "writer", "critic"],
    "execution_order": [["planner"], ["researcher", "coder"], ["writer"], ["critic"]],
    "reasoning": "The task benefits from planning, research, implementation, writing, and critique.",
}


class RouterAgent(BaseAgent):
    """Analyze a task and select the required agents."""

    name = "router"
    system_prompt = (
        "You are a task router for a multi-agent AI system. "
        "Analyze the user task and decide which agents are needed."
    )

    async def run(self, state: AgentOSState) -> dict[str, Any]:
        logs = self.log_start(state)
        memories = self.shared_memory.retrieve(
            "long_term_memory", state["original_task"], n_results=3
        )
        memory_context = "\n".join(memories) or state.get("memory_context", "")
        prompt = f"""
Task: {state["original_task"]}

Relevant memory:
{memory_context or "No relevant memory found."}

Return ONLY JSON in this shape:
{{
  "task_type": "research|code|write|mixed|simple",
  "complexity": "low|medium|high",
  "agents_needed": ["planner","researcher","coder","writer","critic"],
  "execution_order": [["planner"],["researcher","coder"],["writer"],["critic"]],
  "reasoning": "one sentence why"
}}
"""
        raw = await self.ollama_call(prompt, self.system_prompt, temperature=0.1)
        decision = self._parse_decision(raw, state["original_task"])
        return {
            "router_decision": decision,
            "memory_context": memory_context or "No relevant memory found.",
            "agent_logs": self.log_done(logs, json.dumps(decision)),
        }

    def _parse_decision(self, raw: str, task: str) -> dict[str, Any]:
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            parsed = json.loads(match.group(0) if match else raw)
            if not isinstance(parsed, dict):
                raise ValueError("Router response was not an object")
        except Exception:
            parsed = self._heuristic_decision(task)
        return self._normalize(parsed)

    def _heuristic_decision(self, task: str) -> dict[str, Any]:
        lowered = task.lower()
        if any(word in lowered for word in ["code", "app", "api", "python", "javascript"]):
            return {
                "task_type": "code",
                "complexity": "medium",
                "agents_needed": ["planner", "coder", "critic"],
                "execution_order": [["planner"], ["coder"], ["critic"]],
                "reasoning": "The task primarily requires software implementation.",
            }
        if any(word in lowered for word in ["research", "compare", "latest", "find"]):
            return {
                "task_type": "research",
                "complexity": "medium",
                "agents_needed": ["planner", "researcher", "writer", "critic"],
                "execution_order": [["planner"], ["researcher"], ["writer"], ["critic"]],
                "reasoning": "The task needs external information and synthesis.",
            }
        if len(task.split()) < 8:
            return {
                "task_type": "simple",
                "complexity": "low",
                "agents_needed": ["planner", "writer", "critic"],
                "execution_order": [["planner"], ["writer"], ["critic"]],
                "reasoning": "The task is short and can be answered with a compact team.",
            }
        return DEFAULT_DECISION.copy()

    def _normalize(self, decision: dict[str, Any]) -> dict[str, Any]:
        agents = [agent for agent in decision.get("agents_needed", []) if isinstance(agent, str)]
        if "planner" not in agents:
            agents.insert(0, "planner")
        if "critic" not in agents:
            agents.append("critic")
        agents = [agent for agent in agents if agent != "critic"] + ["critic"]
        order = decision.get("execution_order")
        if not isinstance(order, list):
            order = [[agent] for agent in agents]
        normalized_order: list[list[str]] = []
        seen: set[str] = set()
        if "planner" in agents:
            normalized_order.append(["planner"])
            seen.add("planner")
        for group in order:
            if not isinstance(group, list):
                continue
            clean_group = [agent for agent in group if agent in agents and agent != "critic"]
            clean_group = [agent for agent in clean_group if not (agent in seen or seen.add(agent))]
            if clean_group:
                normalized_order.append(clean_group)
        for agent in agents:
            if agent != "critic" and agent not in seen:
                normalized_order.append([agent])
        normalized_order.append(["critic"])
        return {
            "task_type": str(decision.get("task_type", "mixed")),
            "complexity": str(decision.get("complexity", "medium")),
            "agents_needed": agents,
            "execution_order": normalized_order,
            "reasoning": str(decision.get("reasoning", DEFAULT_DECISION["reasoning"])),
        }
