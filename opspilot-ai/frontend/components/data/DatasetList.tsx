"use client";

import { useEffect, useRef } from "react";
import { QualityReportCard } from "./QualityReportCard";
import type { Dataset } from "@/types/dataset";

const STATUS_STYLES: Record<Dataset["status"], string> = {
  completed: "text-status-success",
  processing: "text-status-warning",
  failed: "text-status-danger",
};

export function DatasetList({
  datasets,
  onPollNeeded,
}: {
  datasets: Dataset[];
  onPollNeeded: () => void;
}) {
  const hasProcessing = datasets.some((d) => d.status === "processing");
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (hasProcessing && !intervalRef.current) {
      intervalRef.current = setInterval(onPollNeeded, 2000);
    }
    if (!hasProcessing && intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [hasProcessing, onPollNeeded]);

  if (datasets.length === 0) {
    return (
      <p className="text-sm text-text-muted">
        No datasets uploaded yet — upload a CSV or XLSX file above to get started.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {datasets.map((dataset) => (
        <div key={dataset.id} className="rounded-card border border-border bg-background-card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{dataset.filename}</p>
              <p className="text-xs text-text-muted">
                {dataset.dataset_type} &middot;{" "}
                {new Date(dataset.created_at).toLocaleString()}
              </p>
            </div>
            <span className={`text-xs font-medium uppercase tracking-wide ${STATUS_STYLES[dataset.status]}`}>
              {dataset.status === "processing" ? "Processing..." : dataset.status}
            </span>
          </div>

          {dataset.status === "completed" && dataset.row_count !== null && (
            <p className="mt-2 text-sm text-text-muted">{dataset.row_count} rows imported</p>
          )}

          {dataset.status === "failed" && dataset.error_message && (
            <p className="mt-2 text-sm text-status-danger">{dataset.error_message}</p>
          )}

          {dataset.quality_report && <QualityReportCard report={dataset.quality_report} />}
        </div>
      ))}
    </div>
  );
}
