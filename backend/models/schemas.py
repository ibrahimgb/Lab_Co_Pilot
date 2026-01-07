"""
Pydantic models for request / response schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Optional


# data Module

class UploadDataResponse(BaseModel):
    file_id: str
    filename: str
    columns: list[str]
    row_count: int
    preview: list[dict[str, Any]]


class FilterRequest(BaseModel):
    file_id: Optional[str] = None
    conditions: str = Field(
        ...,
        description="A pandas-compatible query string, e.g. 'age > 30 and gene_A < 0.5'",
    )


class AggregateRequest(BaseModel):
    file_id: Optional[str] = None
    group_column: str
    value_column: str
    agg_func: str = "mean"  # mean, sum, count, min, max, median, std


class PlotRequest(BaseModel):
    file_id: Optional[str] = None
    plot_type: str = "bar"  # bar, pie, scatter, line, histogram, box
    x_column: str
    y_column: Optional[str] = None
    title: Optional[str] = None


class DataResponse(BaseModel):
    data: list[dict[str, Any]]
    columns: list[str]
    row_count: int


class PlotResponse(BaseModel):
    plot_json: str
    plot_type: str


class StatsResponse(BaseModel):
    statistics: dict[str, Any]


# document Module

class DocUploadResponse(BaseModel):
    doc_id: str
    filename: str
    num_chunks: int
    entities: list[dict[str, str]]


class DocSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class DocSearchResult(BaseModel):
    text: str
    document: str
    score: float


class DocSearchResponse(BaseModel):
    results: list[DocSearchResult]


class DocListItem(BaseModel):
    doc_id: str
    name: str
    num_chunks: int


# chat Module

class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    text: str
    plot_json: Optional[str] = None
    table_data: Optional[list[dict[str, Any]]] = None
    table_columns: Optional[list[str]] = None


class ChatHistoryItem(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    plot_json: Optional[str] = None
    table_data: Optional[list[dict[str, Any]]] = None
    table_columns: Optional[list[str]] = None
