"use client";

import { uploadDocument } from "@/lib/api";
import type { DocUploadResponse } from "@/lib/types";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

interface Props {
  onUpload?: (data: DocUploadResponse) => void;
}

export default function DocUploader({ onUpload }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DocUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (files: File[]) => {
      const file = files[0];
      if (!file) return;
      setLoading(true);
      setError(null);
      try {
        const data = await uploadDocument(file);
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
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
  });

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-purple-500 bg-purple-50 dark:bg-purple-950"
            : "border-gray-300 dark:border-gray-600 hover:border-purple-400"
        }`}
      >
        <input {...getInputProps()} />
        {loading ? (
          <p className="text-sm text-gray-500">Processing PDF…</p>
        ) : (
          <div>
            <p className="text-sm font-medium">Drop PDF here</p>
            <p className="text-xs text-gray-400 mt-1">or click to browse</p>
          </div>
        )}
      </div>

      {error && <p className="text-xs text-red-500">{error}</p>}

      {result && (
        <div className="text-xs space-y-1">
          <p className="text-green-600 font-medium">
            ✓ {result.filename} — {result.num_chunks} chunks indexed
          </p>
          {result.entities.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {result.entities.slice(0, 10).map((e, i) => (
                <span
                  key={i}
                  className="px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded text-[10px]"
                >
                  {e.text}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
