import type { InventoryItem } from "@/types/analytics";
import { RiskBadge } from "./RiskBadge";

export function InventoryTable({ items }: { items: InventoryItem[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-text-muted">No inventory records yet.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-card border border-border bg-background-card">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-text-muted">
            <th className="px-4 py-3 font-medium">Product</th>
            <th className="px-4 py-3 font-medium">Category</th>
            <th className="px-4 py-3 font-medium text-right">Stock</th>
            <th className="px-4 py-3 font-medium text-right">Reorder Point</th>
            <th className="px-4 py-3 font-medium">Risk</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b border-border last:border-b-0">
              <td className="px-4 py-3">
                <p>{item.product_name}</p>
                <p className="text-xs text-text-muted">{item.product_sku}</p>
              </td>
              <td className="px-4 py-3 text-text-muted">{item.category}</td>
              <td className="px-4 py-3 text-right">{item.current_stock}</td>
              <td className="px-4 py-3 text-right text-text-muted">{item.reorder_point}</td>
              <td className="px-4 py-3">
                <RiskBadge level={item.risk_level} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
