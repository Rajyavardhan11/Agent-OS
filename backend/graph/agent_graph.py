"""Agent OS orchestration graph."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from langgraph.graph import END, START, StateGraph

try:
    from langgraph.types import Send
except Exception:  # pragma: no cover - compatibility with older installs
    try:
        from langgraph.constants import Send
    except Exception:
        Send = None  # type: ignore[assignment]

from agents.coder import CoderAgent
from agents.critic import CriticAgent
from agents.memory_manager import MemoryManagerAgent
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.router import RouterAgent
from agents.writer import WriterAgent
from graph.state import AgentOSState, initial_state
from memory.shared_memory import SharedMemory

shared_memory = SharedMemory()

AGENTS = {
    "memory_manager": MemoryManagerAgent(shared_memory),
    "router": RouterAgent(shared_memory),
    "planner": PlannerAgent(shared_memory),
    "researcher": ResearcherAgent(shared_memory),
    "coder": CoderAgent(shared_memory),
    "writer": WriterAgent(shared_memory),
    "critic": CriticAgent(shared_memory),
}


def _merge_state(state: AgentOSState, update: dict[str, Any]) -> AgentOSState:
    merged: AgentOSState = {**state, **update}
    if "agent_logs" in update:
        base_logs = state.get("agent_logs", [])
        update_logs = update.get("agent_logs", [])
        base_keys = {
            (log.get("agent"), log.get("timestamp"), log.get("output"))
            for log in base_logs
        }
        merged["agent_logs"] = [
            *base_logs,
            *[
                log
                for log in update_logs
                if (log.get("agent"), log.get("timestamp"), log.get("output")) not in base_keys
            ],
        ]
    if "error_log" in update:
        merged["error_log"] = [*state.get("error_log", []), *update.get("error_log", [])]
    return merged


async def _safe_run_agent(agent_name: str, state: AgentOSState) -> dict[str, Any]:
    agent = AGENTS[agent_name]
    try:
        return await agent.run(state)
    except Exception as exc:
        logs = agent.log_start(state)
        return {
            "agent_logs": agent.log_done(logs, f"Error: {exc}"),
            "error_log": agent.log_error(state, exc),
        }


async def memory_manager_node(state: AgentOSState) -> dict[str, Any]:
    """LangGraph node for memory lookup."""
    return await _safe_run_agent("memory_manager", state)


async def router_node(state: AgentOSState) -> dict[str, Any]:
    """LangGraph node for routing."""
    return await _safe_run_agent("router", state)


async def orchestrator_node(state: AgentOSState) -> dict[str, Any]:
    """Run router-selected parallel groups and converge after each group."""
    working_state = dict(state)
    execution_order = working_state.get("router_decision", {}).get("execution_order", [])
    for group in execution_order:
        agent_group = [
            agent_name
            for agent_name in group
            if agent_name in AGENTS and agent_name not in {"memory_manager", "router"}
        ]
        if not agent_group:
            continue
        if Send is not None:
            _ = [Send(agent_name, working_state) for agent_name in agent_group]
        results = await asyncio.gather(
            *[_safe_run_agent(agent_name, working_state) for agent_name in agent_group],
            return_exceptions=False,
        )
        for result in results:
            working_state = _merge_state(working_state, result)
    return {
        "plan": working_state.get("plan", ""),
        "research": working_state.get("research", ""),
        "code": working_state.get("code", ""),
        "draft": working_state.get("draft", ""),
        "critique": working_state.get("critique", {}),
        "final_output": working_state.get("final_output", ""),
        "agent_logs": working_state.get("agent_logs", []),
        "error_log": working_state.get("error_log", []),
    }


def build_graph() -> Any:
    """Build and compile the Agent OS StateGraph."""
    graph = StateGraph(AgentOSState)
    graph.add_node("memory_manager", memory_manager_node)
    graph.add_node("router", router_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_edge(START, "memory_manager")
    graph.add_edge("memory_manager", "router")
    graph.add_edge("router", "orchestrator")
    graph.add_edge("orchestrator", END)
    return graph.compile()


agent_graph = build_graph()


async def run_task(task_id: str, task: str) -> AgentOSState:
    """Run a task to completion and return final graph state."""
    state = initial_state(task_id, task)
    return await agent_graph.ainvoke(state)


async def stream_task(task_id: str, task: str) -> AsyncIterator[dict[str, Any]]:
    """Stream agent updates as each agent/group completes."""
    state = initial_state(task_id, task)
    for agent_name in ["memory_manager", "router"]:
        yield {
            "agent": agent_name,
            "status": "running",
            "output": "",
            "timestamp": "",
        }
        update = await _safe_run_agent(agent_name, state)
        state = _merge_state(state, update)
        yield state["agent_logs"][-1]

    execution_order = state.get("router_decision", {}).get("execution_order", [])
    for group in execution_order:
        agent_group = [
            agent_name
            for agent_name in group
            if agent_name in AGENTS and agent_name not in {"memory_manager", "router"}
        ]
        if not agent_group:
            continue
        for agent_name in agent_group:
            yield {
                "agent": agent_name,
                "status": "running",
                "output": "",
                "timestamp": "",
            }
        results = await asyncio.gather(
            *[_safe_run_agent(agent_name, state) for agent_name in agent_group],
            return_exceptions=False,
        )
        for result in results:
            state = _merge_state(state, result)
            yield state["agent_logs"][-1]

    yield {
        "agent": "system",
        "status": "done",
        "output": state.get("final_output", ""),
        "timestamp": state["agent_logs"][-1]["timestamp"] if state.get("agent_logs") else "",
        "state": state,
    }
