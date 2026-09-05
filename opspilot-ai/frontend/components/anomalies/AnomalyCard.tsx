import type { Anomaly } from "@/types/ml";

const SEVERITY_STYLES: Record<Anomaly["severity"], string> = {
  critical: "border-status-danger/40 bg-status-danger/5",
  warning: "border-status-warning/40 bg-status-warning/5",
  information: "border-border bg-background-card",
};

const SEVERITY_LABEL_STYLES: Record<Anomaly["severity"], string> = {
  critical: "bg-status-danger/15 text-status-danger",
  warning: "bg-status-warning/15 text-status-warning",
  information: "bg-accent-cyan/10 text-accent-cyan",
};

export function AnomalyCard({ anomaly }: { anomaly: Anomaly }) {
  return (
    <div className={`rounded-card border p-5 ${SEVERITY_STYLES[anomaly.severity]}`}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium capitalize">{anomaly.metric.replace(/_/g, " ")}</p>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium uppercase ${SEVERITY_LABEL_STYLES[anomaly.severity]}`}>
          {anomaly.severity}
        </span>
      </div>
      <p className="mt-2 text-sm text-text-muted">{anomaly.explanation}</p>
      <p className="mt-3 text-sm">
        <span className="text-text-muted">Recommended: </span>
        {anomaly.recommended_action}
      </p>
    </div>
  );
}
