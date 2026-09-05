import type { ExpenseItem } from "@/types/analytics";

export function ExpenseTable({ items }: { items: ExpenseItem[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-text-muted">No expenses recorded yet.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-card border border-border bg-background-card">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-text-muted">
            <th className="px-4 py-3 font-medium">Date</th>
            <th className="px-4 py-3 font-medium">Category</th>
            <th className="px-4 py-3 font-medium">Description</th>
            <th className="px-4 py-3 font-medium text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          {items.map((e) => (
            <tr key={e.id} className="border-b border-border last:border-b-0">
              <td className="px-4 py-3 text-text-muted">{e.expense_date}</td>
              <td className="px-4 py-3 capitalize">{e.category}</td>
              <td className="px-4 py-3 text-text-muted">{e.description ?? "—"}</td>
              <td className="px-4 py-3 text-right font-medium">${e.amount.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
