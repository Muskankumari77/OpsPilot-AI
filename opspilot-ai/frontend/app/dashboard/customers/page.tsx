"use client";

import { useCustomers } from "@/hooks/useCustomers";
import { useChurn } from "@/hooks/useChurn";
import { useSegments } from "@/hooks/useSegments";
import { KPICard } from "@/components/dashboard/KPICard";
import { BreakdownChart } from "@/components/common/BreakdownChart";
import { CustomerTable } from "@/components/customers/CustomerTable";
import { ChurnRiskTable } from "@/components/customers/ChurnRiskTable";
import { SegmentSummary } from "@/components/customers/SegmentSummary";

export default function CustomersPage() {
  const { summary, items, isLoading } = useCustomers();
  const { churn, error: churnError, isLoading: churnLoading } = useChurn();
  const { segments, isLoading: segmentsLoading, isRunning, runSegmentation } = useSegments();

  return (
    <main className="px-6 py-8">
      <h1 className="font-display text-2xl font-semibold">Customer Intelligence</h1>
      <p className="mt-1 text-sm text-text-muted">
        Customer growth, RFM segments, and churn risk with plain-language explanations.
      </p>

      {isLoading && <p className="mt-8 text-sm text-text-muted">Loading customer data...</p>}

      {!isLoading && summary && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
            <KPICard label="Total Customers" value={summary.total_customers.toLocaleString()} accent />
            <KPICard label="New This Month" value={summary.new_customers_this_month.toLocaleString()} />
            <KPICard label="Regions" value={String(summary.by_region.length)} />
          </div>

          <div className="rounded-card border border-border bg-background-card p-5">
            <p className="text-sm font-medium text-text-muted">Customers by Region</p>
            <div className="mt-3">
              <BreakdownChart
                data={summary.by_region.map((r) => ({ label: r.region, value: r.count }))}
                valuePrefix=""
              />
            </div>
          </div>

          {!segmentsLoading && (
            <SegmentSummary segments={segments} isRunning={isRunning} onRun={runSegmentation} />
          )}

          <div>
            <p className="mb-3 text-sm font-medium text-text-muted">
              Churn Risk{" "}
              {churn && (
                <span className="font-normal text-text-muted">
                  — {churn.high_risk_count} of {churn.total_customers_analyzed} customers at high risk
                </span>
              )}
            </p>
            {churnLoading && <p className="text-sm text-text-muted">Training churn model...</p>}
            {churnError && (
              <p className="rounded-lg border border-status-warning/30 bg-status-warning/10 p-3 text-sm text-status-warning">
                {churnError}
              </p>
            )}
            {churn && <ChurnRiskTable customers={churn.customers.slice(0, 10)} />}
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-text-muted">All Customers</p>
            <CustomerTable items={items} />
          </div>
        </div>
      )}
    </main>
  );
}
