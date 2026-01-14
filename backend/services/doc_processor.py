"""
Document processing — PDF text extraction, chunking, entity extraction.
"""

from __future__ import annotations

import io
from typing import Any

import pdfplumber


# ── PDF text extraction ──────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file."""
    buf = io.BytesIO(file_bytes)
    text_parts: list[str] = []
    with pdfplumber.open(buf) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


# ── Text chunking ────────────────────────────────────────────────────────────

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping chunks of roughly `chunk_size` characters.
    """
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if c]


# ── Entity extraction (lightweight, no spaCy required) ───────────────────────

def extract_entities_simple(text: str) -> list[dict[str, str]]:
    """
    Lightweight keyword-based entity extraction.
    Returns a list of {'text': ..., 'label': ...} dicts.
    Falls back gracefully if spaCy or the sci model isn't installed.
    """
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_sci_sm")
        except OSError:
            nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:10000])  # limit to avoid OOM on huge docs
        seen: set[str] = set()
        entities: list[dict[str, str]] = []
        for ent in doc.ents:
            key = (ent.text.lower(), ent.label_)
            if key not in seen:
                seen.add(key)
                entities.append({"text": ent.text, "label": ent.label_})
        return entities[:50]  # cap at 50
    except ImportError:
        return []
