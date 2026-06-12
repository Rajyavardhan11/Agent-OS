"""Task API routes."""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from graph.agent_graph import run_task, shared_memory, stream_task

router = APIRouter(prefix="/api", tags=["tasks"])


class TaskRequest(BaseModel):
    """Incoming task payload."""

    task: str = Field(min_length=1, max_length=2000)


@router.post("/task")
async def create_task(payload: TaskRequest) -> dict[str, Any]:
    """Run a task synchronously and return full state."""
    task = payload.task.strip()
    if not task:
        raise HTTPException(status_code=422, detail="Task cannot be empty")
    task_id = str(uuid4())
    return await run_task(task_id, task)


@router.get("/task/{task_id}/stream")
async def task_stream(task_id: str, task: str) -> EventSourceResponse:
    """Run a task and stream agent updates over SSE."""
    clean_task = task.strip()
    if not clean_task or len(clean_task) > 2000:
        raise HTTPException(status_code=422, detail="Task must be 1-2000 characters")

    async def event_generator() -> Any:
        async for event in stream_task(task_id, clean_task):
            if event.get("agent") == "system":
                yield {
                    "event": "done",
                    "data": json.dumps(
                        {
                            "final_output": event.get("output", ""),
                            "state": event.get("state", {}),
                        }
                    ),
                }
            else:
                yield {"event": "agent", "data": json.dumps(event)}

    return EventSourceResponse(event_generator())


@router.get("/tasks/history")
async def task_history() -> list[dict[str, Any]]:
    """Return recent completed tasks from long-term memory."""
    rows = shared_memory.get_recent("long_term_memory", n=10)
    return [
        {
            "task_id": row["metadata"].get("task_id", ""),
            "original_task": row["metadata"].get("original_task", ""),
            "final_output": row["content"],
            "score": row["metadata"].get("score"),
            "timestamp": row["metadata"].get("timestamp", ""),
        }
        for row in rows
    ]

