import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// data Module

export async function uploadData(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/api/data/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function listDatasets() {
  const res = await api.get("/api/data/list");
  return res.data;
}

export async function filterData(conditions: string, fileId?: string) {
  const res = await api.post("/api/data/filter", {
    conditions,
    file_id: fileId,
  });
  return res.data;
}

export async function aggregateData(
  groupColumn: string,
  valueColumn: string,
  aggFunc: string = "mean",
  fileId?: string
) {
  const res = await api.post("/api/data/aggregate", {
    group_column: groupColumn,
    value_column: valueColumn,
    agg_func: aggFunc,
    file_id: fileId,
  });
  return res.data;
}

export async function describeData(fileId?: string) {
  const res = await api.post("/api/data/describe", null, {
    params: { file_id: fileId },
  });
  return res.data;
}

export async function plotData(
  plotType: string,
  xColumn: string,
  yColumn?: string,
  title?: string,
  fileId?: string
) {
  const res = await api.post("/api/data/plot", {
    plot_type: plotType,
    x_column: xColumn,
    y_column: yColumn,
    title,
    file_id: fileId,
  });
  return res.data;
}

// document Module

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/api/docs/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function searchDocuments(query: string, topK: number = 5) {
  const res = await api.post("/api/docs/search", { query, top_k: topK });
  return res.data;
}

export async function listDocuments() {
  const res = await api.get("/api/docs/list");
  return res.data;
}

// chat Module

export async function sendMessage(message: string) {
  const res = await api.post("/api/chat/message", { message });
  return res.data;
}

export async function getChatHistory() {
  const res = await api.get("/api/chat/history");
  return res.data;
}

export async function clearChat() {
  const res = await api.post("/api/chat/clear");
  return res.data;
}
