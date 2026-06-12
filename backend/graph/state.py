"""Shared LangGraph state schema."""

from __future__ import annotations

from typing import Any, TypedDict


class AgentOSState(TypedDict, total=False):
    task_id: str
    original_task: str
    router_decision: dict[str, Any]
    memory_context: str
    plan: str
    research: str
    code: str
    draft: str
    critique: dict[str, Any]
    final_output: str
    agent_logs: list[dict[str, Any]]
    error_log: list[str]


def initial_state(task_id: str, task: str) -> AgentOSState:
    """Create a complete initial state for graph execution."""
    return {
        "task_id": task_id,
        "original_task": task,
        "router_decision": {},
        "memory_context": "",
        "plan": "",
        "research": "",
        "code": "",
        "draft": "",
        "critique": {},
        "final_output": "",
        "agent_logs": [],
        "error_log": [],
    }

