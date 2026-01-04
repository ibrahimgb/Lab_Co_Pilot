"use client";

import { uploadData } from "@/lib/api";
import type { UploadDataResponse } from "@/lib/types";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import DataTable from "./DataTable";

interface Props {
  onUpload?: (data: UploadDataResponse) => void;
}

export default function DataUploader({ onUpload }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UploadDataResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (files: File[]) => {
      const file = files[0];
      if (!file) return;
      setLoading(true);
      setError(null);
      try {
        const data = await uploadData(file);
        setResult(data);
        onUpload?.(data);
      } catch (err: unknown) {
        const msg =
          err instanceof Error ? err.message : "Upload failed";
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
    },
    maxFiles: 1,
  });

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
            : "border-gray-300 dark:border-gray-600 hover:border-blue-400"
        }`}
      >
        <input {...getInputProps()} />
        {loading ? (
          <p className="text-sm text-gray-500">Uploading…</p>
        ) : (
          <div>
            <p className="text-sm font-medium">
              📊 Drop CSV / Excel here
            </p>
            <p className="text-xs text-gray-400 mt-1">or click to browse</p>
          </div>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}

      {result && (
        <div className="text-xs space-y-1">
          <p className="text-green-600 font-medium">
            ✓ {result.filename} — {result.row_count} rows, {result.columns.length} columns
          </p>
          <DataTable
            data={result.preview}
            columns={result.columns}
            maxRows={5}
          />
        </div>
      )}
    </div>
  );
}
