"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { UploadForm } from "@/components/data/UploadForm";
import { DatasetList } from "@/components/data/DatasetList";
import { SummaryCard } from "@/components/data/SummaryCard";
import type { Dataset, DatasetSummary } from "@/types/dataset";

export default function DataPage() {
  const { activeOrgId } = useAuth();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [summary, setSummary] = useState<DatasetSummary | null>(null);

  const refresh = useCallback(() => {
    if (!activeOrgId) return;
    apiFetch<Dataset[]>("/datasets").then(setDatasets).catch(() => {});
    apiFetch<DatasetSummary>("/datasets/summary").then(setSummary).catch(() => {});
  }, [activeOrgId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <main className="px-6 py-8">
      <div className="max-w-3xl space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold">Data</h1>
          <p className="mt-1 text-sm text-text-muted">
            Upload sales, customer, product, inventory, or expense data — or
            run <code className="text-accent-cyan">python -m scripts.generate_demo_data</code>{" "}
            from the backend to seed a full demo dataset instantly.
          </p>
        </div>

        {summary && <SummaryCard summary={summary} />}

        <UploadForm onUploaded={(d) => setDatasets((prev) => [d, ...prev])} />

        <div>
          <p className="mb-3 text-sm font-medium text-text-muted">Upload history</p>
          <DatasetList datasets={datasets} onPollNeeded={refresh} />
        </div>
      </div>
    </main>
  );
}
