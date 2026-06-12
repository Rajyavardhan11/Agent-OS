"""Persistent shared vector memory backed by ChromaDB."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

import chromadb
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

from config import CHROMA_PERSIST_PATH, EMBEDDING_MODEL


class SharedMemory:
    """Singleton vector memory shared by all agents."""

    _instance: "SharedMemory | None" = None
    _lock = Lock()

    def __new__(cls) -> "SharedMemory":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
        try:
            self.embedding_model: SentenceTransformer | None = SentenceTransformer(
                EMBEDDING_MODEL,
                local_files_only=True,
            )
        except Exception:
            self.embedding_model = None
        self.collections = {
            "task_memory": self.client.get_or_create_collection("task_memory"),
            "long_term_memory": self.client.get_or_create_collection("long_term_memory"),
        }
        self._initialized = True

    def _collection(self, collection_name: str) -> Collection:
        if collection_name not in self.collections:
            raise ValueError(f"Unknown collection: {collection_name}")
        return self.collections[collection_name]

    def _embed(self, text: str) -> list[float]:
        if self.embedding_model is None:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            return [byte / 255 for byte in digest[:32]]
        embedding = self.embedding_model.encode(text)
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return list(embedding)

    def store(
        self,
        collection_name: str,
        task_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store content in a collection and return its memory id."""
        if not content.strip():
            return ""
        memory_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        merged_metadata = {
            "task_id": task_id,
            "timestamp": timestamp,
            **(metadata or {}),
        }
        collection = self._collection(collection_name)
        collection.add(
            ids=[memory_id],
            embeddings=[self._embed(content)],
            documents=[content],
            metadatas=[merged_metadata],
        )
        return memory_id

    def retrieve(
        self,
        collection_name: str,
        query: str,
        n_results: int = 3,
        task_id: str | None = None,
    ) -> list[str]:
        """Retrieve relevant memories as plain text documents."""
        if not query.strip():
            return []
        where = {"task_id": task_id} if task_id else None
        try:
            result = self._collection(collection_name).query(
                query_embeddings=[self._embed(query)],
                n_results=n_results,
                where=where,
                include=["documents"],
            )
        except Exception:
            return []
        documents = result.get("documents", [[]])
        return [item for item in documents[0] if item]

    def get_recent(self, collection_name: str, n: int = 10) -> list[dict[str, Any]]:
        """Return the most recent memory entries with metadata."""
        result = self._collection(collection_name).get(include=["documents", "metadatas"])
        documents = result.get("documents", [])
        metadatas = result.get("metadatas", [])
        rows = [
            {"content": doc, "metadata": metadata or {}}
            for doc, metadata in zip(documents, metadatas, strict=False)
        ]
        rows.sort(key=lambda row: str(row["metadata"].get("timestamp", "")), reverse=True)
        return rows[:n]

    def clear_task(self, task_id: str) -> None:
        """Delete task-scoped memories for a task."""
        collection = self._collection("task_memory")
        matches = collection.get(where={"task_id": task_id})
        ids = matches.get("ids", [])
        if ids:
            collection.delete(ids=ids)

    def clear_all(self) -> None:
        """Reset all memory collections."""
        for name in list(self.collections):
            try:
                self.client.delete_collection(name)
            except Exception:
                pass
            self.collections[name] = self.client.get_or_create_collection(name)
