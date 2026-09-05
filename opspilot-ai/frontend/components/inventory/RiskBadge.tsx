const RISK_STYLES: Record<string, string> = {
  Critical: "bg-status-danger/15 text-status-danger",
  High: "bg-status-danger/10 text-status-danger",
  Medium: "bg-status-warning/15 text-status-warning",
  Low: "bg-accent-cyan/10 text-accent-cyan",
  Healthy: "bg-status-success/15 text-status-success",
};

export function RiskBadge({ level }: { level: string }) {
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${RISK_STYLES[level] ?? ""}`}>
      {level}
    </span>
  );
}
