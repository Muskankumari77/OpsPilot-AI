"use client";

import { useAlerts } from "@/hooks/useAlerts";
import type { AlertItem } from "@/types/operations";

const TYPE_STYLES: Record<AlertItem["type"], string> = {
  critical: "border-status-danger/40 bg-status-danger/5",
  warning: "border-status-warning/40 bg-status-warning/5",
  information: "border-border bg-background-card",
  success: "border-status-success/40 bg-status-success/5",
};

export default function AlertsPage() {
  const { alerts, isLoading, markRead } = useAlerts();

  return (
    <main className="px-6 py-8">
      <h1 className="font-display text-2xl font-semibold">Alerts</h1>
      <p className="mt-1 text-sm text-text-muted">
        Real-time notifications synced from current anomalies and risk levels.
      </p>

      {isLoading && <p className="mt-8 text-sm text-text-muted">Loading alerts...</p>}

      {!isLoading && alerts.length === 0 && (
        <p className="mt-8 text-sm text-text-muted">No alerts right now.</p>
      )}

      {!isLoading && alerts.length > 0 && (
        <div className="mt-6 space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`rounded-card border p-4 ${TYPE_STYLES[alert.type]} ${alert.is_read ? "opacity-60" : ""}`}
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">{alert.title}</p>
                {!alert.is_read && (
                  <button
                    onClick={() => markRead(alert.id)}
                    className="text-xs text-accent-cyan hover:underline"
                  >
                    Mark read
                  </button>
                )}
              </div>
              <p className="mt-1 text-sm text-text-muted">{alert.message}</p>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
