import type { DatasetSummary } from "@/types/dataset";

export function SummaryCard({ summary }: { summary: DatasetSummary }) {
  const rows: { label: string; value: number }[] = [
    { label: "Products", value: summary.products },
    { label: "Customers", value: summary.customers },
    { label: "Sales", value: summary.sales },
    { label: "Inventory", value: summary.inventory },
    { label: "Expenses", value: summary.expenses },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
      {rows.map((row) => (
        <div key={row.label} className="rounded-card border border-border bg-background-card p-4 text-center">
          <p className="font-display text-2xl font-semibold">{row.value.toLocaleString()}</p>
          <p className="mt-1 text-xs text-text-muted">{row.label}</p>
        </div>
      ))}
    </div>
  );
}
