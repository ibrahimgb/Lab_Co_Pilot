"""
Restricted sandbox for executing LLM-generated Pandas/Plotly code.
"""

from __future__ import annotations

import signal
import traceback
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.io as pio


class SandboxTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise SandboxTimeout("Code execution timed out (10s limit).")


def execute_code(
    code: str,
    df: pd.DataFrame,
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    """
    Execute LLM-generated Python code in a restricted namespace.

    The code has access to:
      - `df` (the current DataFrame)
      - `pd` (pandas)
      - `px` (plotly.express)

    It should produce either:
      - `result` — a DataFrame, dict, string, or number
      - `fig` — a Plotly figure

    Returns: {"result": ..., "plot_json": ..., "error": ...}
    """
    allowed_globals: dict[str, Any] = {
        "__builtins__": {
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "bool": bool,
            "True": True,
            "False": False,
            "None": None,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "print": print,
            "isinstance": isinstance,
            "type": type,
        },
        "pd": pd,
        "px": px,
        "df": df.copy(),
    }
    local_vars: dict[str, Any] = {}

    # Set a timeout (Unix only)
    old_handler = None
    try:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout_seconds)
    except (AttributeError, ValueError):
        pass  # Windows or non-main thread — skip alarm

    output: dict[str, Any] = {"result": None, "plot_json": None, "error": None}

    try:
        exec(code, allowed_globals, local_vars)

        # Extract results
        if "fig" in local_vars:
            fig = local_vars["fig"]
            output["plot_json"] = pio.to_json(fig)

        if "result" in local_vars:
            res = local_vars["result"]
            if isinstance(res, pd.DataFrame):
                output["result"] = {
                    "data": res.head(100).fillna("").to_dict(orient="records"),
                    "columns": list(res.columns),
                    "row_count": len(res),
                }
            elif isinstance(res, pd.Series):
                output["result"] = res.to_dict()
            else:
                output["result"] = res

    except SandboxTimeout:
        output["error"] = "Code execution timed out (10s limit)."
    except Exception:
        output["error"] = traceback.format_exc()
    finally:
        try:
            signal.alarm(0)
            if old_handler is not None:
                signal.signal(signal.SIGALRM, old_handler)
        except (AttributeError, ValueError):
            pass

    return output
