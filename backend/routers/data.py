"""
Data analysis router — file upload, filtering, aggregation, stats, plotting.
"""

from __future__ import annotations

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

import store
from services.data_engine import (
    load_file,
    filter_data,
    aggregate_data,
    describe_data,
    generate_plot,
)
from models.schemas import (
    UploadDataResponse,
    FilterRequest,
    AggregateRequest,
    PlotRequest,
    DataResponse,
    PlotResponse,
    StatsResponse,
)

router = APIRouter()


def _get_df(file_id: str | None):
    """Resolve a DataFrame from the store."""
    fid = file_id or store.active_dataset_id
    if not fid or fid not in store.data_frames:
        raise HTTPException(status_code=404, detail="No dataset found. Upload a file first.")
    return fid, store.data_frames[fid]


# ── Upload ───────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadDataResponse)
async def upload_data(file: UploadFile = File(...)):
    """Upload a CSV or Excel file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")
    try:
        contents = await file.read()
        df = load_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    file_id = uuid.uuid4().hex[:12]
    store.data_frames[file_id] = df
    store.data_meta[file_id] = {
        "filename": file.filename,
        "columns": list(df.columns),
        "row_count": len(df),
    }
    store.active_dataset_id = file_id

    preview = df.head(5).fillna("").to_dict(orient="records")
    return UploadDataResponse(
        file_id=file_id,
        filename=file.filename,
        columns=list(df.columns),
        row_count=len(df),
        preview=preview,
    )


# ── List datasets ───────────────────────────────────────────────────────────

@router.get("/list")
def list_datasets():
    """Return metadata for all uploaded datasets."""
    return {
        "datasets": [
            {"file_id": fid, **meta}
            for fid, meta in store.data_meta.items()
        ],
        "active_dataset_id": store.active_dataset_id,
    }


# ── Filter ───────────────────────────────────────────────────────────────────

@router.post("/filter", response_model=DataResponse)
def filter_endpoint(req: FilterRequest):
    """Filter the active dataset with a pandas query string."""
    fid, df = _get_df(req.file_id)
    try:
        result = filter_data(df, req.conditions)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Filter error: {e}")
    return DataResponse(
        data=result.head(100).fillna("").to_dict(orient="records"),
        columns=list(result.columns),
        row_count=len(result),
    )


# ── Aggregate ────────────────────────────────────────────────────────────────

@router.post("/aggregate", response_model=DataResponse)
def aggregate_endpoint(req: AggregateRequest):
    """Group & aggregate the active dataset."""
    fid, df = _get_df(req.file_id)
    try:
        result = aggregate_data(df, req.group_column, req.value_column, req.agg_func)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Aggregation error: {e}")
    return DataResponse(
        data=result.fillna("").to_dict(orient="records"),
        columns=list(result.columns),
        row_count=len(result),
    )


# ── Describe ─────────────────────────────────────────────────────────────────

@router.post("/describe", response_model=StatsResponse)
def describe_endpoint(file_id: str | None = None):
    """Return descriptive statistics for the active dataset."""
    fid, df = _get_df(file_id)
    stats = describe_data(df)
    return StatsResponse(statistics=stats)


# ── Plot ─────────────────────────────────────────────────────────────────────

@router.post("/plot", response_model=PlotResponse)
def plot_endpoint(req: PlotRequest):
    """Generate a Plotly chart from the active dataset."""
    fid, df = _get_df(req.file_id)
    try:
        plot_json = generate_plot(
            df,
            plot_type=req.plot_type,
            x_col=req.x_column,
            y_col=req.y_column,
            title=req.title,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Plot error: {e}")
    return PlotResponse(plot_json=plot_json, plot_type=req.plot_type)
