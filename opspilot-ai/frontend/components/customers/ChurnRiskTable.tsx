import type { ChurnRiskCustomer } from "@/types/ml";

function riskColor(probability: number) {
  if (probability >= 0.6) return "text-status-danger";
  if (probability >= 0.35) return "text-status-warning";
  return "text-status-success";
}

export function ChurnRiskTable({ customers }: { customers: ChurnRiskCustomer[] }) {
  if (customers.length === 0) {
    return <p className="text-sm text-text-muted">No churn risk data yet.</p>;
  }

  return (
    <div className="space-y-3">
      {customers.map((c) => (
        <div key={c.customer_id} className="rounded-card border border-border bg-background-card p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">{c.customer_name}</p>
            <p className={`text-sm font-semibold ${riskColor(c.churn_probability)}`}>
              {Math.round(c.churn_probability * 100)}% churn risk
            </p>
          </div>
          <ul className="mt-2 space-y-1">
            {c.top_factors.map((f, i) => (
              <li key={i} className="text-xs text-text-muted">
                • {f.description}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
