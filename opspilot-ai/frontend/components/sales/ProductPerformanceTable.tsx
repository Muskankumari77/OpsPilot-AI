import type { ProductPerformance } from "@/types/analytics";

export function ProductPerformanceTable({
  title,
  products,
}: {
  title: string;
  products: ProductPerformance[];
}) {
  return (
    <div className="rounded-card border border-border bg-background-card p-5">
      <p className="text-sm font-medium text-text-muted">{title}</p>
      {products.length === 0 ? (
        <p className="mt-3 text-sm text-text-muted">No data in this period yet.</p>
      ) : (
        <table className="mt-3 w-full text-sm">
          <tbody>
            {products.map((p) => (
              <tr key={p.product_id} className="border-t border-border first:border-t-0">
                <td className="py-2 pr-2">{p.product_name}</td>
                <td className="py-2 pr-2 text-right text-text-muted">{p.units_sold} units</td>
                <td className="py-2 text-right font-medium">${p.revenue.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
