import pytest

from agents.router import RouterAgent
from graph.state import initial_state
from memory.shared_memory import SharedMemory


def fresh_router() -> RouterAgent:
    SharedMemory._instance = None
    return RouterAgent(SharedMemory())


@pytest.mark.asyncio
async def test_router_returns_valid_json_for_code_task(monkeypatch) -> None:
    router = fresh_router()

    async def fake_ollama(*args, **kwargs):
        return '{"task_type":"code","complexity":"medium","agents_needed":["planner","coder","critic"],"execution_order":[["planner"],["coder"],["critic"]],"reasoning":"Needs code."}'

    monkeypatch.setattr(router, "ollama_call", fake_ollama)
    result = await router.run(initial_state("task-1", "Build a Python API"))

    assert result["router_decision"]["task_type"] == "code"
    assert result["router_decision"]["execution_order"][-1] == ["critic"]


@pytest.mark.asyncio
async def test_router_fallback_when_ollama_returns_invalid_json(monkeypatch) -> None:
    router = fresh_router()

    async def fake_ollama(*args, **kwargs):
        return "not json"

    monkeypatch.setattr(router, "ollama_call", fake_ollama)
    result = await router.run(initial_state("task-1", "Research vector databases"))

    assert result["router_decision"]["task_type"] == "research"
    assert "researcher" in result["router_decision"]["agents_needed"]


def test_critic_always_added_as_last_agent() -> None:
    router = fresh_router()
    decision = router._normalize(
        {
            "task_type": "write",
            "complexity": "low",
            "agents_needed": ["writer", "planner"],
            "execution_order": [["writer"], ["planner"]],
            "reasoning": "Needs writing.",
        }
    )

    assert decision["agents_needed"][-1] == "critic"
    assert decision["execution_order"][-1] == ["critic"]

