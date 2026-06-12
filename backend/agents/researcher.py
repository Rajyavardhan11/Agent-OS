"""Researcher agent."""

from __future__ import annotations

import re
from typing import Any

from agents.base_agent import BaseAgent
from graph.state import AgentOSState
from tools.search import TavilySearchTool


class ResearcherAgent(BaseAgent):
    """Perform web research and summarize results."""

    name = "researcher"
    system_prompt = (
        "You are a research specialist. Find accurate, relevant information "
        "to support task completion."
    )

    def __init__(self, shared_memory) -> None:  # type: ignore[no-untyped-def]
        super().__init__(shared_memory)
        self.search_tool = TavilySearchTool()

    async def run(self, state: AgentOSState) -> dict[str, Any]:
        logs = self.log_start(state)
        query_prompt = f"Create 2-3 concise web search queries for this plan:\n{state.get('plan', '')}"
        raw_queries = await self.ollama_call(query_prompt, self.system_prompt, temperature=0.2)
        queries = self._extract_queries(raw_queries) or [state["original_task"]]
        search_blocks: list[str] = []
        for query in queries[:3]:
            results = self.search_tool.search(query, max_results=3)
            formatted = "\n".join(
                f"- {item['title']} ({item['url']}): {item['content']}" for item in results
            )
            search_blocks.append(f"Query: {query}\n{formatted}")
        summary_prompt = f"""
Task: {state["original_task"]}
Plan: {state.get("plan", "")}

Search results:
{chr(10).join(search_blocks)}

Write a coherent research brief with concise bullet points and source URLs when available.
"""
        summary = await self.ollama_call(summary_prompt, self.system_prompt, temperature=0.4)
        if summary == "Ollama not available":
            summary = "\n\n".join(search_blocks)
        self.shared_memory.store("task_memory", state["task_id"], summary, {"agent": self.name})
        return {"research": summary, "agent_logs": self.log_done(logs, summary)}

    def _extract_queries(self, raw: str) -> list[str]:
        lines = [re.sub(r"^[\-\d\.\)\s]+", "", line).strip() for line in raw.splitlines()]
        return [line.strip('"') for line in lines if 4 <= len(line) <= 140]

