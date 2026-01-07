"""
In-memory data store for the Lab Co-Pilot application.
Holds uploaded DataFrames, conversation history, and document metadata.
"""

from __future__ import annotations

import pandas as pd
from typing import Any

# ── Data store ───────────────────────────────────────────────────────────────
# Key = file_id (str), Value = pandas DataFrame
data_frames: dict[str, pd.DataFrame] = {}

# Metadata about uploaded data files (original filename, columns, row count)
data_meta: dict[str, dict[str, Any]] = {}

# The "active" dataset id that the chat/LLM will operate on by default
active_dataset_id: str | None = None

# ── Document store ───────────────────────────────────────────────────────────
# Key = doc_id (str), Value = {"name": str, "num_chunks": int, "entities": [...]}
document_meta: dict[str, dict[str, Any]] = {}

# ── Chat history ─────────────────────────────────────────────────────────────
conversation_history: list[dict[str, Any]] = []


def clear_all() -> None:
    """Reset everything – useful for testing."""
    data_frames.clear()
    data_meta.clear()
    document_meta.clear()
    conversation_history.clear()
    global active_dataset_id
    active_dataset_id = None
