"use client";

import ChatPanel from "@/components/ChatPanel";
import DataUploader from "@/components/DataUploader";
import DocUploader from "@/components/DocUploader";
import { listDatasets, listDocuments } from "@/lib/api";
import type { DatasetMeta, DocListItem, DocUploadResponse, UploadDataResponse } from "@/lib/types";
import { useEffect, useState } from "react";

export default function Home() {
  const [datasets, setDatasets] = useState<DatasetMeta[]>([]);
  const [documents, setDocuments] = useState<DocListItem[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    listDatasets()
      .then((res) => setDatasets(res.datasets || []))
      .catch(() => {});
    listDocuments()
      .then((res) => setDocuments(res.documents || []))
      .catch(() => {});
  }, []);

  const handleDataUpload = (data: UploadDataResponse) => {
    setDatasets((prev) => [
      ...prev.filter((d) => d.file_id !== data.file_id),
      {
        file_id: data.file_id,
        filename: data.filename,
        columns: data.columns,
        row_count: data.row_count,
      },
    ]);
  };

  const handleDocUpload = (data: DocUploadResponse) => {
    setDocuments((prev) => [
      ...prev.filter((d) => d.doc_id !== data.doc_id),
      {
        doc_id: data.doc_id,
        name: data.filename,
        num_chunks: data.num_chunks,
      },
    ]);
  };

  return (
    <div className="flex h-screen bg-white dark:bg-gray-950">
      {/* ── sidebar  */}
      <aside
        className={`${
          sidebarOpen ? "w-80" : "w-0"
        } transition-all duration-200 overflow-hidden border-r border-gray-200 dark:border-gray-800 flex flex-col`}
      >
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <h1 className="text-lg font-bold flex items-center gap-2">
            🔬 Lab Co-Pilot
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Your AI lab assistant
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* data upload section */}
          <section>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Data Files
            </h3>
            <DataUploader onUpload={handleDataUpload} />
            {datasets.length > 0 && (
              <div className="mt-2 space-y-1">
                {datasets.map((d) => (
                  <div
                    key={d.file_id}
                    className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 rounded px-2 py-1"
                  >
                    <span>📊</span>
                    <span className="truncate flex-1">{d.filename}</span>
                    <span className="text-gray-400">
                      {d.row_count}r × {d.columns.length}c
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* document upload section */}
          <section>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Documents
            </h3>
            <DocUploader onUpload={handleDocUpload} />
            {documents.length > 0 && (
              <div className="mt-2 space-y-1">
                {documents.map((d) => (
                  <div
                    key={d.doc_id}
                    className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 rounded px-2 py-1"
                  >
                    <span>📄</span>
                    <span className="truncate flex-1">{d.name}</span>
                    <span className="text-gray-400">{d.num_chunks} chunks</span>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </aside>

      {/* ── Main  */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* top bar */}
        <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-200 dark:border-gray-800">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1"
            aria-label="Toggle sidebar"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
          <span className="text-sm text-gray-400">
            {datasets.length > 0
              ? `Active: ${datasets[datasets.length - 1].filename}`
              : "No dataset loaded"}
          </span>
        </div>

        {/* chat panel */}
        <div className="flex-1 min-h-0">
          <ChatPanel />
        </div>
      </main>
    </div>
  );
}
