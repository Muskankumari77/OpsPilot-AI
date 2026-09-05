import type { CustomerItem } from "@/types/analytics";

export function CustomerTable({ items }: { items: CustomerItem[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-text-muted">No customers yet.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-card border border-border bg-background-card">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-text-muted">
            <th className="px-4 py-3 font-medium">Name</th>
            <th className="px-4 py-3 font-medium">Email</th>
            <th className="px-4 py-3 font-medium">Region</th>
            <th className="px-4 py-3 font-medium">Segment</th>
          </tr>
        </thead>
        <tbody>
          {items.map((c) => (
            <tr key={c.id} className="border-b border-border last:border-b-0">
              <td className="px-4 py-3">{c.name}</td>
              <td className="px-4 py-3 text-text-muted">{c.email}</td>
              <td className="px-4 py-3 text-text-muted">{c.region}</td>
              <td className="px-4 py-3">
                {c.segment ?? (
                  <span className="text-xs text-text-muted">Not yet analyzed</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
