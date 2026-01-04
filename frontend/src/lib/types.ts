// data Module

export interface UploadDataResponse {
  file_id: string;
  filename: string;
  columns: string[];
  row_count: number;
  preview: Record<string, unknown>[];
}

export interface DatasetMeta {
  file_id: string;
  filename: string;
  columns: string[];
  row_count: number;
}

export interface DataResponse {
  data: Record<string, unknown>[];
  columns: string[];
  row_count: number;
}

export interface PlotResponse {
  plot_json: string;
  plot_type: string;
}

export interface StatsResponse {
  statistics: Record<string, unknown>;
}

// document Module

export interface DocUploadResponse {
  doc_id: string;
  filename: string;
  num_chunks: number;
  entities: { text: string; label: string }[];
}

export interface DocSearchResult {
  text: string;
  document: string;
  score: number;
}

export interface DocListItem {
  doc_id: string;
  name: string;
  num_chunks: number;
}

// chat Module
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  plot_json?: string | null;
  table_data?: Record<string, unknown>[] | null;
  table_columns?: string[] | null;
}

export interface ChatMessageResponse {
  text: string;
  plot_json?: string | null;
  table_data?: Record<string, unknown>[] | null;
  table_columns?: string[] | null;
}
