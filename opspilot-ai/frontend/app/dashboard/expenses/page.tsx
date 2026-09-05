"use client";

import { useExpenses } from "@/hooks/useExpenses";
import { KPICard } from "@/components/dashboard/KPICard";
import { BreakdownChart } from "@/components/common/BreakdownChart";
import { ExpenseTrendChart } from "@/components/expenses/ExpenseTrendChart";
import { ExpenseTable } from "@/components/expenses/ExpenseTable";

export default function ExpensesPage() {
  const { summary, items, isLoading } = useExpenses();

  return (
    <main className="px-6 py-8">
      <h1 className="font-display text-2xl font-semibold">Expense Intelligence</h1>
      <p className="mt-1 text-sm text-text-muted">
        Spend by category and how it&apos;s trending over the last quarter.
      </p>

      {isLoading && <p className="mt-8 text-sm text-text-muted">Loading expense data...</p>}

      {!isLoading && summary && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
            <KPICard
              label="Total Expenses"
              value={`$${summary.total_expenses.toLocaleString()}`}
              growthPct={summary.month_over_month_change_pct}
              accent
            />
            <KPICard label="Categories" value={String(summary.by_category.length)} />
            <KPICard
              label="Period"
              value={`${summary.period_start} → ${summary.period_end}`}
            />
          </div>

          <div className="rounded-card border border-border bg-background-card p-5">
            <p className="text-sm font-medium text-text-muted">Expense Trend</p>
            <div className="mt-3">
              <ExpenseTrendChart data={summary.trend} />
            </div>
          </div>

          <div className="rounded-card border border-border bg-background-card p-5">
            <p className="text-sm font-medium text-text-muted">Spend by Category</p>
            <div className="mt-3">
              <BreakdownChart
                data={summary.by_category.map((c) => ({ label: c.category, value: c.amount }))}
              />
            </div>
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-text-muted">Recent Expenses</p>
            <ExpenseTable items={items} />
          </div>
        </div>
      )}
    </main>
  );
}
