"""
Knowledge base — ChromaDB-backed vector store for document search.
"""

from __future__ import annotations

import os
import chromadb
from chromadb.config import Settings

# ── Initialize ChromaDB ─────────────────────────────────────────────────────

_chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")


def _get_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=_chroma_path)


def _get_collection(client: chromadb.ClientAPI):
    return client.get_or_create_collection(
        name="lab_docs",
        metadata={"hnsw:space": "cosine"},
    )


# ── Add document chunks ─────────────────────────────────────────────────────

def add_document(doc_id: str, doc_name: str, chunks: list[str]) -> int:
    """
    Embed and store document chunks in ChromaDB.
    Returns the number of chunks stored.
    """
    if not chunks:
        return 0

    client = _get_client()
    collection = _get_collection(client)

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"document": doc_name, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas,
    )
    return len(chunks)


# ── Search ───────────────────────────────────────────────────────────────────

def search(query: str, top_k: int = 5) -> list[dict]:
    """
    Semantic search across all indexed documents.
    Returns list of {text, document, score}.
    """
    client = _get_client()
    collection = _get_collection(client)

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
    )

    hits: list[dict] = []
    if results and results["documents"]:
        for i, doc_text in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if results["distances"] else 0.0
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            hits.append({
                "text": doc_text,
                "document": metadata.get("document", "unknown"),
                "score": round(1 - distance, 4),  # cosine similarity
            })
    return hits


# ── List documents ───────────────────────────────────────────────────────────

def list_documents() -> list[str]:
    """Return names of all indexed documents."""
    client = _get_client()
    collection = _get_collection(client)
    if collection.count() == 0:
        return []
    # Get unique document names from metadata
    all_meta = collection.get(include=["metadatas"])
    names: set[str] = set()
    if all_meta and all_meta["metadatas"]:
        for m in all_meta["metadatas"]:
            if m and "document" in m:
                names.add(m["document"])
    return sorted(names)
