"""Critic agent."""

from __future__ import annotations

import json
import re
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentOSState


class CriticAgent(BaseAgent):
    """Evaluate and improve the final output."""

    name = "critic"
    system_prompt = (
        "You are a ruthless quality critic. Improve outputs to be accurate, "
        "complete, and excellent."
    )

    async def run(self, state: AgentOSState) -> dict[str, Any]:
        logs = self.log_start(state)
        source_output = state.get("draft") or state.get("code") or state.get("research") or state.get("plan", "")
        prompt = f"""
Original task: {state["original_task"]}
Draft: {state.get("draft", "")}
Code: {state.get("code", "")}

Review for accuracy, completeness, clarity, and structure.
Return ONLY this JSON:
{{
  "score": 8,
  "issues": ["issue1", "issue2"],
  "improvements_made": ["what was fixed"],
  "improved_output": "complete improved markdown output here"
}}
"""
        raw = await self.ollama_call(prompt, self.system_prompt, temperature=0.25)
        critique = self._parse(raw, source_output)
        final_output = str(critique.get("improved_output", source_output))
        self.shared_memory.store(
            "long_term_memory",
            state["task_id"],
            final_output,
            {
                "agent": self.name,
                "original_task": state["original_task"],
                "score": int(critique.get("score", 7)),
            },
        )
        return {
            "critique": critique,
            "final_output": final_output,
            "agent_logs": self.log_done(logs, final_output),
        }

    def _parse(self, raw: str, fallback_output: str) -> dict[str, Any]:
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            parsed = json.loads(match.group(0) if match else raw)
            if not isinstance(parsed, dict):
                raise ValueError("Critic response was not an object")
            parsed.setdefault("score", 7)
            parsed.setdefault("issues", [])
            parsed.setdefault("improvements_made", [])
            parsed.setdefault("improved_output", fallback_output)
            return parsed
        except Exception:
            return {
                "score": 7,
                "issues": ["Critic JSON parsing failed or Ollama was unavailable."],
                "improvements_made": ["Returned the strongest available agent output."],
                "improved_output": fallback_output,
            }

