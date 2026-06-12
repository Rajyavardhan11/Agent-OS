import pytest

from graph.agent_graph import AGENTS, run_task


@pytest.mark.asyncio
async def test_full_graph_runs_end_to_end_with_simple_task(monkeypatch) -> None:
    async def fake_ollama(self, prompt, system_prompt, temperature=0.7):
        if self.name == "router":
            return '{"task_type":"simple","complexity":"low","agents_needed":["planner","writer","critic"],"execution_order":[["planner"],["writer"],["critic"]],"reasoning":"Simple task."}'
        if self.name == "critic":
            return '{"score":9,"issues":[],"improvements_made":["Polished output"],"improved_output":"Final answer"}'
        return f"{self.name} output"

    for agent in AGENTS.values():
        monkeypatch.setattr(agent, "ollama_call", fake_ollama.__get__(agent, agent.__class__))

    result = await run_task("task-1", "Say hello")

    assert result["final_output"] == "Final answer"
    assert result["critique"]["score"] == 9


@pytest.mark.asyncio
async def test_parallel_agents_both_complete(monkeypatch) -> None:
    async def fake_ollama(self, prompt, system_prompt, temperature=0.7):
        if self.name == "router":
            return '{"task_type":"mixed","complexity":"high","agents_needed":["planner","researcher","coder","critic"],"execution_order":[["planner"],["researcher","coder"],["critic"]],"reasoning":"Mixed task."}'
        if self.name == "critic":
            return '{"score":8,"issues":[],"improvements_made":[],"improved_output":"Done"}'
        return f"{self.name} output"

    for agent in AGENTS.values():
        monkeypatch.setattr(agent, "ollama_call", fake_ollama.__get__(agent, agent.__class__))

    result = await run_task("task-2", "Research and code")
    completed_agents = {log["agent"] for log in result["agent_logs"] if log["status"] == "done"}

    assert {"researcher", "coder"}.issubset(completed_agents)


@pytest.mark.asyncio
async def test_error_in_one_agent_does_not_crash_graph(monkeypatch) -> None:
    async def broken_run(state):
        raise RuntimeError("boom")

    monkeypatch.setattr(AGENTS["coder"], "run", broken_run)

    async def fake_ollama(self, prompt, system_prompt, temperature=0.7):
        if self.name == "router":
            return '{"task_type":"code","complexity":"medium","agents_needed":["planner","coder","critic"],"execution_order":[["planner"],["coder"],["critic"]],"reasoning":"Code task."}'
        if self.name == "critic":
            return '{"score":6,"issues":["Coder failed"],"improvements_made":[],"improved_output":"Recovered"}'
        return f"{self.name} output"

    for name, agent in AGENTS.items():
        if name != "coder":
            monkeypatch.setattr(agent, "ollama_call", fake_ollama.__get__(agent, agent.__class__))

    result = await run_task("task-3", "Build code")

    assert result["final_output"] == "Recovered"
    assert any("coder: boom" in error for error in result["error_log"])

