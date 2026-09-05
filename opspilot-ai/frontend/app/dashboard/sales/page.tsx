"use client";

import { useState } from "react";
import { useSales, type SalesFilters } from "@/hooks/useSales";
import { KPICard } from "@/components/dashboard/KPICard";
import { RevenueChart } from "@/components/sales/RevenueChart";
import { SalesFilterBar } from "@/components/sales/SalesFilterBar";
import { ProductPerformanceTable } from "@/components/sales/ProductPerformanceTable";
import { BreakdownChart } from "@/components/common/BreakdownChart";
import { PRODUCT_CATEGORIES, REGIONS } from "@/lib/constants";

export default function SalesPage() {
  const [filters, setFilters] = useState<SalesFilters>({});
  const { summary, trends, isLoading } = useSales(filters);

  return (
    <main className="px-6 py-8">
      <h1 className="font-display text-2xl font-semibold">Sales Intelligence</h1>
      <p className="mt-1 text-sm text-text-muted">
        Revenue, orders, and product performance — filterable by region, category, and date.
      </p>

      <div className="mt-5">
        <SalesFilterBar
          filters={filters}
          onChange={setFilters}
          regions={REGIONS}
          categories={PRODUCT_CATEGORIES}
        />
      </div>

      {isLoading && <p className="mt-8 text-sm text-text-muted">Loading sales data...</p>}

      {!isLoading && summary && trends && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <KPICard
              label="Total Revenue"
              value={`$${summary.total_revenue.toLocaleString()}`}
              growthPct={summary.revenue_growth_pct}
              accent
            />
            <KPICard
              label="Orders"
              value={summary.total_orders.toLocaleString()}
              growthPct={summary.orders_growth_pct}
            />
            <KPICard label="Avg Order Value" value={`$${summary.average_order_value.toLocaleString()}`} />
            <KPICard label="Profit Margin" value={`${summary.profit_margin_pct}%`} />
          </div>

          <div className="rounded-card border border-border bg-background-card p-5">
            <p className="text-sm font-medium text-text-muted">Revenue Over Time</p>
            <div className="mt-3">
              <RevenueChart data={trends.revenue_over_time} />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="rounded-card border border-border bg-background-card p-5">
              <p className="text-sm font-medium text-text-muted">Revenue by Category</p>
              <div className="mt-3">
                <BreakdownChart
                  data={trends.revenue_by_category.map((c) => ({ label: c.category, value: c.revenue }))}
                />
              </div>
            </div>
            <div className="rounded-card border border-border bg-background-card p-5">
              <p className="text-sm font-medium text-text-muted">Revenue by Region</p>
              <div className="mt-3">
                <BreakdownChart
                  data={trends.revenue_by_region.map((r) => ({ label: r.region, value: r.revenue }))}
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <ProductPerformanceTable title="Top Products" products={trends.top_products} />
            <ProductPerformanceTable title="Worst-Performing Products" products={trends.worst_products} />
          </div>
        </div>
      )}
    </main>
  );
}
