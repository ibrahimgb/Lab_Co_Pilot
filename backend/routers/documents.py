"""
Documents router — PDF upload, search, and listing.
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

import store
from services.doc_processor import extract_text_from_pdf, chunk_text, extract_entities_simple
from services.knowledge_base import (
    add_document,
    search as kb_search,
    list_documents,
)
from models.schemas import (
    DocUploadResponse,
    DocSearchRequest,
    DocSearchResponse,
    DocSearchResult,
    DocListItem,
)

router = APIRouter()


# upload PDF

@router.post("/upload", response_model=DocUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF, extract text, chunk, embed, and index."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        contents = await file.read()
        text = extract_text_from_pdf(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract any text from the PDF.")

    chunks = chunk_text(text)
    entities = extract_entities_simple(text)

    doc_id = uuid.uuid4().hex[:12]
    num_chunks = add_document(doc_id, file.filename, chunks)

    store.document_meta[doc_id] = {
        "name": file.filename,
        "num_chunks": num_chunks,
        "entities": entities,
    }

    return DocUploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        num_chunks=num_chunks,
        entities=entities[:20],
    )


# search

@router.post("/search", response_model=DocSearchResponse)
def search_documents(req: DocSearchRequest):
    """Semantic search across all indexed documents."""
    results = kb_search(req.query, top_k=req.top_k)
    return DocSearchResponse(
        results=[DocSearchResult(**r) for r in results]
    )


# list 

@router.get("/list")
def list_docs():
    """Return all indexed documents."""
    doc_names = list_documents()
    items = []
    for doc_id, meta in store.document_meta.items():
        items.append(DocListItem(
            doc_id=doc_id,
            name=meta["name"],
            num_chunks=meta["num_chunks"],
        ))
    return {"documents": items}
