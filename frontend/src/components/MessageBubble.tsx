"use client";

import type { ChatMessage } from "@/lib/types";
import ReactMarkdown from "react-markdown";
import DataTable from "./DataTable";
import PlotViewer from "./PlotViewer";

interface Props {
  message: ChatMessage;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-md"
        }`}
      >
        {/* Text content */}
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Embedded plot */}
        {message.plot_json && (
          <div className="mt-3">
            <PlotViewer plotJson={message.plot_json} />
          </div>
        )}

        {/* Embedded table */}
        {message.table_data &&
          message.table_columns &&
          message.table_data.length > 0 && (
            <div className="mt-3">
              <DataTable
                data={message.table_data}
                columns={message.table_columns}
                maxRows={20}
              />
            </div>
          )}
      </div>
    </div>
  );
}
