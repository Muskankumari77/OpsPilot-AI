"use client";

import { useAnomalies } from "@/hooks/useAnomalies";
import { AnomalyCard } from "@/components/anomalies/AnomalyCard";

export default function AnomaliesPage() {
  const { anomalies, isLoading } = useAnomalies();

  return (
    <main className="px-6 py-8">
      <h1 className="font-display text-2xl font-semibold">Anomalies</h1>
      <p className="mt-1 text-sm text-text-muted">
        Unusual revenue months, expense spikes, and outlier transactions — detected
        via z-score analysis and Isolation Forest.
      </p>

      {isLoading && <p className="mt-8 text-sm text-text-muted">Scanning for anomalies...</p>}

      {!isLoading && anomalies.length === 0 && (
        <p className="mt-8 text-sm text-text-muted">No anomalies detected — everything looks within normal range.</p>
      )}

      {!isLoading && anomalies.length > 0 && (
        <div className="mt-6 space-y-3">
          {anomalies.map((a, i) => (
            <AnomalyCard key={`${a.metric}-${a.period}-${i}`} anomaly={a} />
          ))}
        </div>
      )}
    </main>
  );
}
