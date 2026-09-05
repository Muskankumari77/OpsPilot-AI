interface KPICardProps {
  label: string;
  value: string;
  growthPct?: number | null;
  accent?: boolean;
}

export function KPICard({ label, value, growthPct, accent }: KPICardProps) {
  const showGrowth = growthPct !== null && growthPct !== undefined;
  const isPositive = (growthPct ?? 0) >= 0;

  return (
    <div
      className={`rounded-card border border-border p-5 ${
        accent
          ? "bg-gradient-to-br from-accent-indigo/15 to-accent-violet/10"
          : "bg-background-card"
      }`}
    >
      <p className="text-sm text-text-muted">{label}</p>
      <p className="mt-2 font-display text-2xl font-semibold">{value}</p>
      {showGrowth && (
        <p className={`mt-1 text-xs ${isPositive ? "text-status-success" : "text-status-danger"}`}>
          {isPositive ? "▲" : "▼"} {Math.abs(growthPct as number)}% vs previous period
        </p>
      )}
    </div>
  );
}
