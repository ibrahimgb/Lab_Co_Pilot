"""
Lab Co-Pilot — FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Lab Co-Pilot API",
    description="Natural-language lab assistant for data analysis, document Q&A, and visualization.",
    version="0.1.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
from routers.data import router as data_router        # noqa: E402
from routers.documents import router as documents_router  # noqa: E402
from routers.chat import router as chat_router        # noqa: E402

app.include_router(data_router, prefix="/api/data", tags=["Data Analysis"])
app.include_router(documents_router, prefix="/api/docs", tags=["Documents"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
def root():
    return {"message": "Lab Co-Pilot API is running."}


@app.get("/health")
def health():
    return {"status": "ok"}
