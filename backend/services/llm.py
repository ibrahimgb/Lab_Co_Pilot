"""
LLM service — Mistral API integration with tool/function calling.
"""

from __future__ import annotations

import json
import os
from typing import Any

from mistralai import Mistral

import store
from services.data_engine import (
    filter_data,
    aggregate_data,
    describe_data,
    generate_plot,
)
from services.knowledge_base import search as kb_search
from services.sandbox import execute_code

# mistral client

_api_key = os.getenv("MISTRAL_API_KEY", "")
_model = "mistral-large-latest"


def _get_client() -> Mistral:
    if not _api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY is not set. Add it to backend/.env"
        )
    return Mistral(api_key=_api_key)


# tool definitions for Mistral function calling 

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "filter_data",
            "description": "Filter the currently loaded dataset using a pandas query string. Example: 'age > 30 and gene_A < 0.5'",
            "parameters": {
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "string",
                        "description": "Pandas query string for filtering rows",
                    }
                },
                "required": ["conditions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aggregate_data",
            "description": "Group the dataset by a column and compute an aggregation (mean, sum, count, min, max, median, std) on another column.",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_column": {
                        "type": "string",
                        "description": "Column to group by",
                    },
                    "value_column": {
                        "type": "string",
                        "description": "Column to aggregate",
                    },
                    "agg_func": {
                        "type": "string",
                        "enum": ["mean", "sum", "count", "min", "max", "median", "std"],
                        "description": "Aggregation function",
                    },
                },
                "required": ["group_column", "value_column", "agg_func"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_data",
            "description": "Get summary statistics (count, mean, std, min, max, etc.) for the active dataset.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_plot",
            "description": "Create a visualization (chart) from the active dataset. Supported types: bar, pie, scatter, line, histogram, box.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_type": {
                        "type": "string",
                        "enum": ["bar", "pie", "scatter", "line", "histogram", "box"],
                        "description": "Type of chart to generate",
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Column for x-axis (or names for pie chart)",
                    },
                    "y_column": {
                        "type": "string",
                        "description": "Column for y-axis (or values for pie chart). Optional for histogram.",
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title",
                    },
                },
                "required": ["plot_type", "x_column"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search uploaded research papers / PDF documents for information related to a query. Uses semantic search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default 5)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_pandas_code",
            "description": "Execute custom Pandas/Plotly Python code on the active dataset. The DataFrame is available as `df`. Store results in `result` variable and/or Plotly figures in `fig` variable.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Use `df` for the DataFrame. Put results in `result` (any type) or `fig` (Plotly figure).",
                    }
                },
                "required": ["code"],
            },
        },
    },
]


# build system prompt

def _build_system_prompt() -> str:
    dataset_info = ""
    if store.active_dataset_id and store.active_dataset_id in store.data_frames:
        df = store.data_frames[store.active_dataset_id]
        meta = store.data_meta.get(store.active_dataset_id, {})
        dataset_info = (
            f"\n\nCurrently loaded dataset: '{meta.get('filename', 'unknown')}'\n"
            f"Columns: {list(df.columns)}\n"
            f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
            f"Data types: {dict(df.dtypes.astype(str))}\n"
            f"Sample (first 3 rows):\n{df.head(3).to_string()}\n"
        )

    doc_info = ""
    doc_names = [m["name"] for m in store.document_meta.values()]
    if doc_names:
        doc_info = f"\n\nUploaded documents: {doc_names}\n"

    return f"""You are Lab Co-Pilot, a helpful assistant for laboratory researchers.
You help users analyze experimental data, create visualizations, and answer questions about uploaded research documents.

You have access to the following tools:
- filter_data: Filter the active dataset
- aggregate_data: Group and aggregate data
- describe_data: Get summary statistics
- generate_plot: Create charts (bar, pie, scatter, line, histogram, box)
- search_documents: Search uploaded PDF documents
- execute_pandas_code: Run custom Pandas code on the dataset

Guidelines:
- When the user asks to visualize data, use generate_plot with the appropriate chart type.
- When the user asks questions about their data, use the data tools.
- When the user asks about research papers or scientific topics, use search_documents.
- For complex analyses, use execute_pandas_code.
- Always explain your results in clear, non-technical language.
- If no dataset is loaded, tell the user to upload one first.
{dataset_info}{doc_info}"""


# tool execution 

def _execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool call and return the result."""

    if name == "filter_data":
        if not store.active_dataset_id:
            return {"error": "No dataset loaded."}
        df = store.data_frames[store.active_dataset_id]
        result = filter_data(df, args["conditions"])
        return {
            "data": result.head(50).fillna("").to_dict(orient="records"),
            "columns": list(result.columns),
            "row_count": len(result),
        }

    elif name == "aggregate_data":
        if not store.active_dataset_id:
            return {"error": "No dataset loaded."}
        df = store.data_frames[store.active_dataset_id]
        result = aggregate_data(
            df,
            args["group_column"],
            args["value_column"],
            args.get("agg_func", "mean"),
        )
        return {
            "data": result.fillna("").to_dict(orient="records"),
            "columns": list(result.columns),
            "row_count": len(result),
        }

    elif name == "describe_data":
        if not store.active_dataset_id:
            return {"error": "No dataset loaded."}
        df = store.data_frames[store.active_dataset_id]
        return describe_data(df)

    elif name == "generate_plot":
        if not store.active_dataset_id:
            return {"error": "No dataset loaded."}
        df = store.data_frames[store.active_dataset_id]
        plot_json = generate_plot(
            df,
            plot_type=args["plot_type"],
            x_col=args["x_column"],
            y_col=args.get("y_column"),
            title=args.get("title"),
        )
        return {"plot_json": plot_json, "plot_type": args["plot_type"]}

    elif name == "search_documents":
        results = kb_search(args["query"], top_k=args.get("top_k", 5))
        return {"results": results}

    elif name == "execute_pandas_code":
        if not store.active_dataset_id:
            return {"error": "No dataset loaded."}
        df = store.data_frames[store.active_dataset_id]
        return execute_code(args["code"], df)

    else:
        return {"error": f"Unknown tool: {name}"}


# ── Main chat function ───────────────────────────────────────────────────────

def chat(user_message: str) -> dict[str, Any]:
    """
    Process a user message:
    1. Send to Mistral with tools
    2. Execute any tool calls
    3. Return final response with optional plot/table
    """
    client = _get_client()

    # Build messages
    messages = [{"role": "system", "content": _build_system_prompt()}]

    # Add conversation history (last 20 messages)
    for h in store.conversation_history[-20:]:
        messages.append({"role": h["role"], "content": h["content"]})

    messages.append({"role": "user", "content": user_message})

    # Store user message in history
    store.conversation_history.append({"role": "user", "content": user_message})

    response_data: dict[str, Any] = {
        "text": "",
        "plot_json": None,
        "table_data": None,
        "table_columns": None,
    }

    try:
        # First LLM call — may include tool calls
        response = client.chat.complete(
            model=_model,
            messages=messages,
            tools=TOOLS,
        )

        assistant_msg = response.choices[0].message

        # Process tool calls if any
        if assistant_msg.tool_calls:
            # Add assistant message with tool calls to messages
            messages.append(assistant_msg)

            for tool_call in assistant_msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                tool_result = _execute_tool(fn_name, fn_args)

                # Extract plot/table from tool result
                if "plot_json" in tool_result and tool_result["plot_json"]:
                    response_data["plot_json"] = tool_result["plot_json"]

                if "data" in tool_result and isinstance(tool_result["data"], list):
                    response_data["table_data"] = tool_result["data"]
                    response_data["table_columns"] = tool_result.get("columns", [])

                if "result" in tool_result and isinstance(tool_result.get("result"), dict):
                    inner = tool_result["result"]
                    if "data" in inner:
                        response_data["table_data"] = inner["data"]
                        response_data["table_columns"] = inner.get("columns", [])

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "name": fn_name,
                    "content": json.dumps(tool_result, default=str),
                    "tool_call_id": tool_call.id,
                })

            # Second LLM call — generate final response with tool results
            response = client.chat.complete(
                model=_model,
                messages=messages,
            )
            response_data["text"] = response.choices[0].message.content or ""

        else:
            response_data["text"] = assistant_msg.content or ""

    except Exception as e:
        response_data["text"] = f"I encountered an error: {str(e)}"

    # Store assistant response in history
    store.conversation_history.append({
        "role": "assistant",
        "content": response_data["text"],
        "plot_json": response_data["plot_json"],
        "table_data": response_data["table_data"],
        "table_columns": response_data["table_columns"],
    })

    return response_data
