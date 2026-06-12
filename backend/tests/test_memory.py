from memory.shared_memory import SharedMemory


def fresh_memory() -> SharedMemory:
    SharedMemory._instance = None
    return SharedMemory()


def test_store_and_retrieve_works_correctly() -> None:
    memory = fresh_memory()
    memory.store("long_term_memory", "task-1", "FastAPI agents use shared memory")

    result = memory.retrieve("long_term_memory", "FastAPI agents", n_results=1)

    assert result == ["FastAPI agents use shared memory"]


def test_clear_task_only_clears_that_task() -> None:
    memory = fresh_memory()
    memory.store("task_memory", "task-1", "first")
    memory.store("task_memory", "task-2", "second")

    memory.clear_task("task-1")

    assert memory.retrieve("task_memory", "x", task_id="task-1") == []
    assert memory.retrieve("task_memory", "x", task_id="task-2") == ["second"]


def test_clear_all_resets_collections() -> None:
    memory = fresh_memory()
    memory.store("long_term_memory", "task-1", "persisted")

    memory.clear_all()

    assert memory.get_recent("long_term_memory") == []

