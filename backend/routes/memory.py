"""Memory API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from graph.agent_graph import shared_memory

router = APIRouter(prefix="/api", tags=["memory"])


@router.get("/memory")
async def get_memory() -> list[dict[str, Any]]:
    """Return recent long-term memories."""
    rows = shared_memory.get_recent("long_term_memory", n=20)
    return [
        {
            "task_id": row["metadata"].get("task_id", ""),
            "task": row["metadata"].get("original_task", ""),
            "content": row["content"],
            "score": row["metadata"].get("score"),
            "timestamp": row["metadata"].get("timestamp", ""),
        }
        for row in rows
    ]


@router.delete("/memory")
async def clear_memory() -> dict[str, bool]:
    """Clear all ChromaDB collections."""
    shared_memory.clear_all()
    return {"cleared": True}

