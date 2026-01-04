"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface Props {
  plotJson: string;
}

export default function PlotViewer({ plotJson }: Props) {
  const figure = useMemo(() => {
    try {
      return JSON.parse(plotJson);
    } catch {
      return null;
    }
  }, [plotJson]);

  if (!figure) {
    return <p className="text-xs text-red-400">Invalid plot data.</p>;
  }

  return (
    <div className="w-full rounded-lg overflow-hidden bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
      <Plot
        data={figure.data}
        layout={{
          ...figure.layout,
          autosize: true,
          margin: { l: 40, r: 20, t: 40, b: 40 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { size: 11 },
        }}
        config={{ responsive: true, displayModeBar: true }}
        useResizeHandler
        style={{ width: "100%", height: "350px" }}
      />
    </div>
  );
}
