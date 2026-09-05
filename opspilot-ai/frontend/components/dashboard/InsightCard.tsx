import type { InsightCard as InsightCardType } from "@/types/operations";

const SEVERITY_STYLES: Record<string, string> = {
  critical: "border-status-danger/40 bg-status-danger/5",
  warning: "border-status-warning/40 bg-status-warning/5",
  information: "border-border bg-background-card",
};

export function InsightCard({ insight }: { insight: InsightCardType }) {
  return (
    <div className={`rounded-card border p-5 ${SEVERITY_STYLES[insight.severity] ?? "border-border bg-background-card"}`}>
      <p className="text-sm font-medium">{insight.title}</p>
      <p className="mt-1 text-sm text-text-muted">{insight.explanation}</p>
      <p className="mt-2 text-xs text-text-muted">{insight.supporting_metric}</p>
      <p className="mt-3 text-sm">
        <span className="text-text-muted">Recommended: </span>
        {insight.recommendation}
      </p>
    </div>
  );
}
