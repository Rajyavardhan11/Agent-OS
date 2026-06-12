"""Offline test fixtures for Agent OS."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


class FakeCollection:
    def __init__(self, name: str) -> None:
        self.name = name
        self.rows: dict[str, dict[str, Any]] = {}

    def add(self, ids, embeddings, documents, metadatas) -> None:  # type: ignore[no-untyped-def]
        for item_id, embedding, document, metadata in zip(ids, embeddings, documents, metadatas, strict=False):
            self.rows[item_id] = {
                "embedding": embedding,
                "document": document,
                "metadata": metadata,
            }

    def query(self, query_embeddings, n_results, where=None, include=None):  # type: ignore[no-untyped-def]
        documents = []
        for row in self.rows.values():
            if where and any(row["metadata"].get(key) != value for key, value in where.items()):
                continue
            documents.append(row["document"])
        return {"documents": [documents[:n_results]]}

    def get(self, where=None, include=None):  # type: ignore[no-untyped-def]
        ids = []
        documents = []
        metadatas = []
        for item_id, row in self.rows.items():
            if where and any(row["metadata"].get(key) != value for key, value in where.items()):
                continue
            ids.append(item_id)
            documents.append(row["document"])
            metadatas.append(row["metadata"])
        return {"ids": ids, "documents": documents, "metadatas": metadatas}

    def delete(self, ids) -> None:  # type: ignore[no-untyped-def]
        for item_id in ids:
            self.rows.pop(item_id, None)


class FakePersistentClient:
    collections: dict[str, FakeCollection] = {}

    def __init__(self, path: str) -> None:
        self.path = path

    def get_or_create_collection(self, name: str) -> FakeCollection:
        self.collections.setdefault(name, FakeCollection(name))
        return self.collections[name]

    def delete_collection(self, name: str) -> None:
        self.collections.pop(name, None)


class FakeSentenceTransformer:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def encode(self, text: str):
        return [float(len(text) % 10), 1.0, 0.5]


chromadb_module = types.ModuleType("chromadb")
chromadb_module.PersistentClient = FakePersistentClient
collection_module = types.ModuleType("chromadb.api.models.Collection")
collection_module.Collection = FakeCollection
sentence_module = types.ModuleType("sentence_transformers")
sentence_module.SentenceTransformer = FakeSentenceTransformer

sys.modules.setdefault("chromadb", chromadb_module)
sys.modules.setdefault("chromadb.api", types.ModuleType("chromadb.api"))
sys.modules.setdefault("chromadb.api.models", types.ModuleType("chromadb.api.models"))
sys.modules.setdefault("chromadb.api.models.Collection", collection_module)
sys.modules.setdefault("sentence_transformers", sentence_module)


@pytest.fixture(autouse=True)
def reset_fake_collections() -> None:
    FakePersistentClient.collections = {}

