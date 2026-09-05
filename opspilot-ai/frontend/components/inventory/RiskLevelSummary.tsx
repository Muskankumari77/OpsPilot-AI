import type { RiskLevelCount } from "@/types/analytics";
import { RiskBadge } from "./RiskBadge";

export function RiskLevelSummary({ counts }: { counts: RiskLevelCount[] }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
      {counts.map((c) => (
        <div key={c.risk_level} className="rounded-card border border-border bg-background-card p-4 text-center">
          <p className="font-display text-2xl font-semibold">{c.count}</p>
          <div className="mt-2">
            <RiskBadge level={c.risk_level} />
          </div>
        </div>
      ))}
    </div>
  );
}
