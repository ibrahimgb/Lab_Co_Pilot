"""
Data analysis engine — Pandas operations & Plotly chart generation.
"""

from __future__ import annotations

import io
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.io as pio


# ── File loading ─────────────────────────────────────────────────────────────

def load_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Load a CSV or Excel file into a DataFrame."""
    buf = io.BytesIO(file_bytes)
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        df = pd.read_csv(buf)
    elif ext in ("xls", "xlsx"):
        df = pd.read_excel(buf, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: .{ext}")
    return df


# ── Filtering ────────────────────────────────────────────────────────────────

def filter_data(df: pd.DataFrame, query_str: str) -> pd.DataFrame:
    """
    Filter a DataFrame using a pandas query string.
    Example: "age > 30 and gene_A < 0.5"
    """
    return df.query(query_str)


# ── Aggregation ──────────────────────────────────────────────────────────────

ALLOWED_AGG_FUNCS = {"mean", "sum", "count", "min", "max", "median", "std"}


def aggregate_data(
    df: pd.DataFrame,
    group_column: str,
    value_column: str,
    agg_func: str = "mean",
) -> pd.DataFrame:
    """Group by a column and aggregate another column."""
    if agg_func not in ALLOWED_AGG_FUNCS:
        raise ValueError(f"Unsupported aggregation: {agg_func}. Use one of {ALLOWED_AGG_FUNCS}")
    result = df.groupby(group_column)[value_column].agg(agg_func).reset_index()
    result.columns = [group_column, f"{value_column}_{agg_func}"]
    return result


# ── Descriptive statistics ───────────────────────────────────────────────────

def describe_data(df: pd.DataFrame) -> dict[str, Any]:
    """Return summary statistics for the DataFrame."""
    desc = df.describe(include="all").fillna("").to_dict()
    info: dict[str, Any] = {
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "statistics": desc,
    }
    return info


# ── Plotting ─────────────────────────────────────────────────────────────────

def generate_plot(
    df: pd.DataFrame,
    plot_type: str,
    x_col: str,
    y_col: str | None = None,
    title: str | None = None,
) -> str:
    """
    Generate a Plotly figure and return its JSON string.
    Supported types: bar, pie, scatter, line, histogram, box.
    """
    plot_type = plot_type.lower()
    chart_title = title or f"{plot_type.capitalize()} chart"

    if plot_type == "pie":
        # For pie, x_col = names, y_col = values
        if y_col:
            agg = df.groupby(x_col)[y_col].sum().reset_index()
            fig = px.pie(agg, names=x_col, values=y_col, title=chart_title)
        else:
            counts = df[x_col].value_counts().reset_index()
            counts.columns = [x_col, "count"]
            fig = px.pie(counts, names=x_col, values="count", title=chart_title)

    elif plot_type == "bar":
        if y_col:
            agg = df.groupby(x_col)[y_col].mean().reset_index()
            fig = px.bar(agg, x=x_col, y=y_col, title=chart_title)
        else:
            counts = df[x_col].value_counts().reset_index()
            counts.columns = [x_col, "count"]
            fig = px.bar(counts, x=x_col, y="count", title=chart_title)

    elif plot_type == "scatter":
        if not y_col:
            raise ValueError("Scatter plot requires both x and y columns.")
        fig = px.scatter(df, x=x_col, y=y_col, title=chart_title)

    elif plot_type == "line":
        if not y_col:
            raise ValueError("Line plot requires both x and y columns.")
        fig = px.line(df, x=x_col, y=y_col, title=chart_title)

    elif plot_type == "histogram":
        fig = px.histogram(df, x=x_col, title=chart_title)

    elif plot_type == "box":
        if y_col:
            fig = px.box(df, x=x_col, y=y_col, title=chart_title)
        else:
            fig = px.box(df, y=x_col, title=chart_title)

    else:
        raise ValueError(
            f"Unsupported plot type: {plot_type}. "
            "Use one of: bar, pie, scatter, line, histogram, box."
        )

    return pio.to_json(fig)
