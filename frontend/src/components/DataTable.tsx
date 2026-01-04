"use client";

interface Props {
  data: Record<string, unknown>[];
  columns: string[];
  maxRows?: number;
}

export default function DataTable({ data, columns, maxRows }: Props) {
  const rows = maxRows ? data.slice(0, maxRows) : data;

  if (!data.length || !columns.length) {
    return <p className="text-xs text-gray-400">No data to display.</p>;
  }

  return (
    <div className="overflow-x-auto rounded border border-gray-200 dark:border-gray-700">
      <table className="min-w-full text-xs">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            {columns.map((col) => (
              <th
                key={col}
                className="px-3 py-1.5 text-left font-semibold text-gray-600 dark:text-gray-300 whitespace-nowrap"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className="border-t border-gray-100 dark:border-gray-700 even:bg-gray-50 dark:even:bg-gray-800/50"
            >
              {columns.map((col) => (
                <td
                  key={col}
                  className="px-3 py-1 whitespace-nowrap text-gray-700 dark:text-gray-300"
                >
                  {String(row[col] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {maxRows && data.length > maxRows && (
        <p className="text-[10px] text-gray-400 px-3 py-1">
          Showing {maxRows} of {data.length} rows
        </p>
      )}
    </div>
  );
}
