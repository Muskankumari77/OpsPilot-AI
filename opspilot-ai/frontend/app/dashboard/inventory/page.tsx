"use client";

import { useState } from "react";
import { useInventory } from "@/hooks/useInventory";
import { KPICard } from "@/components/dashboard/KPICard";
import { RiskLevelSummary } from "@/components/inventory/RiskLevelSummary";
import { InventoryTable } from "@/components/inventory/InventoryTable";

export default function InventoryPage() {
  const [understockedOnly, setUnderstockedOnly] = useState(false);
  const { summary, items, isLoading } = useInventory(understockedOnly);

  const atRiskCount = summary?.by_risk_level
    .filter((r) => r.risk_level === "Critical" || r.risk_level === "High")
    .reduce((sum, r) => sum + r.count, 0);

  return (
    <main className="px-6 py-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Inventory Intelligence</h1>
          <p className="mt-1 text-sm text-text-muted">
            Stock levels and stock-out risk across every product.
          </p>
        </div>
        <label className="flex items-center gap-2 text-sm text-text-muted">
          <input
            type="checkbox"
            checked={understockedOnly}
            onChange={(e) => setUnderstockedOnly(e.target.checked)}
            className="accent-accent-indigo"
          />
          Understocked only
        </label>
      </div>

      {isLoading && <p className="mt-8 text-sm text-text-muted">Loading inventory data...</p>}

      {!isLoading && summary && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
            <KPICard label="Total Products" value={summary.total_products.toLocaleString()} accent />
            <KPICard
              label="Inventory Value"
              value={`$${summary.total_inventory_value.toLocaleString()}`}
            />
            <KPICard label="Products at Risk" value={String(atRiskCount ?? 0)} />
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-text-muted">Risk Breakdown</p>
            <RiskLevelSummary counts={summary.by_risk_level} />
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-text-muted">
              {understockedOnly ? "Understocked Products" : "All Inventory"}
            </p>
            <InventoryTable items={items} />
          </div>
        </div>
      )}
    </main>
  );
}
