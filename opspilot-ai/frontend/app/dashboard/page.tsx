"use client";

import { useAuth } from "@/hooks/useAuth";
import { useDashboard } from "@/hooks/useDashboard";
import { useInsights } from "@/hooks/useInsights";
import { BusinessHealthCard } from "@/components/dashboard/BusinessHealthCard";
import { KPICard } from "@/components/dashboard/KPICard";
import { InsightCard } from "@/components/dashboard/InsightCard";
import {
  ArrowUpRight,
  Sparkles,
  Users,
  ShoppingCart,
  Wallet,
  Package,
} from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const { summary, isLoading } = useDashboard();
  const {
    insights,
    isLoading: insightsLoading,
  } = useInsights();

  const firstName =
    user?.full_name?.split(" ")[0] ?? "there";

  return (
    <main className="dashboard-grid min-h-[calc(100vh-76px)] px-5 py-7 lg:px-8">
      {/* HEADER */}

      <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
        <div>
          <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-accent-primary/10 px-3 py-1.5 text-xs font-semibold text-accent-primary">
            <Sparkles size={13} />
            AI business intelligence
          </div>

          <h1 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
            Good to see you,{" "}
            <span className="gradient-text">
              {firstName}!
            </span>{" "}
            👋
          </h1>

          <p className="mt-2 text-sm text-text-muted">
            Here&apos;s how your business is performing
            over the last 30 days.
          </p>
        </div>

        <button className="flex w-fit items-center gap-2 rounded-xl border border-border bg-white px-4 py-2.5 text-sm font-medium shadow-sm">
          Last 30 days
          <ArrowUpRight size={15} />
        </button>
      </div>

      {isLoading && (
        <div className="mt-10 rounded-3xl border border-border bg-white p-10 text-center shadow-soft">
          <Sparkles className="mx-auto animate-pulse text-accent-primary" />
          <p className="mt-3 text-sm text-text-muted">
            Analyzing your business...
          </p>
        </div>
      )}

      {!isLoading && summary && (
        <div className="mt-8 space-y-6">
          {/* KPI */}

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-3xl border border-border bg-white p-5 shadow-soft">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-text-muted">
                    Revenue
                  </p>

                  <p className="mt-2 text-3xl font-bold">
                    ${summary.revenue.value.toLocaleString()}
                  </p>

                  <p className="mt-2 text-xs font-semibold text-status-success">
                    ↑ {summary.revenue.growth_pct ?? 0}% vs last period
                  </p>
                </div>

                <div className="rounded-2xl bg-status-success/10 p-3">
                  <Wallet
                    size={20}
                    className="text-status-success"
                  />
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-border bg-white p-5 shadow-soft">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-text-muted">
                    Orders
                  </p>

                  <p className="mt-2 text-3xl font-bold">
                    {summary.orders.value.toLocaleString()}
                  </p>

                  <p className="mt-2 text-xs font-semibold text-status-success">
                    ↑ {summary.orders.growth_pct ?? 0}%
                  </p>
                </div>

                <div className="rounded-2xl bg-accent-blue/10 p-3">
                  <ShoppingCart
                    size={20}
                    className="text-accent-blue"
                  />
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-border bg-white p-5 shadow-soft">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-text-muted">
                    Gross Profit
                  </p>

                  <p className="mt-2 text-3xl font-bold">
                    ${summary.profit.value.toLocaleString()}
                  </p>

                  <p className="mt-2 text-xs font-semibold text-accent-pink">
                    Margin {summary.profit_margin_pct}%
                  </p>
                </div>

                <div className="rounded-2xl bg-accent-pink/10 p-3">
                  <TrendingUpIcon />
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-border bg-white p-5 shadow-soft">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-text-muted">
                    Customers
                  </p>

                  <p className="mt-2 text-3xl font-bold">
                    {summary.total_customers.toLocaleString()}
                  </p>

                  <p className="mt-2 text-xs font-semibold text-accent-primary">
                    +{summary.new_customers_this_month} this month
                  </p>
                </div>

                <div className="rounded-2xl bg-accent-primary/10 p-3">
                  <Users
                    size={20}
                    className="text-accent-primary"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* HEALTH + SECONDARY */}

          <div className="grid gap-5 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <BusinessHealthCard
                score={summary.business_health_score}
              />
            </div>

            <div className="rounded-3xl border border-border bg-white p-6 shadow-soft">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-status-warning/10 p-3">
                  <Package
                    size={20}
                    className="text-status-warning"
                  />
                </div>

                <div>
                  <p className="text-sm text-text-muted">
                    Inventory at risk
                  </p>

                  <p className="text-2xl font-bold">
                    {summary.understocked_products}
                  </p>
                </div>
              </div>

              <p className="mt-4 text-sm text-text-muted">
                Products below their recommended reorder
                point.
              </p>
            </div>
          </div>

          {/* AI INSIGHTS */}

          <section>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <Sparkles
                    size={17}
                    className="text-accent-primary"
                  />

                  <h2 className="font-display text-lg font-bold">
                    AI Insights
                  </h2>
                </div>

                <p className="mt-1 text-xs text-text-muted">
                  What OpsPilot thinks you should know.
                </p>
              </div>
            </div>

            {insightsLoading && (
              <div className="rounded-3xl border border-border bg-white p-6 text-sm text-text-muted">
                AI is analyzing your data...
              </div>
            )}

            {!insightsLoading &&
              insights.length === 0 && (
                <div className="rounded-3xl border border-border bg-white p-6 text-sm text-text-muted">
                  No notable insights right now.
                </div>
              )}

            {!insightsLoading &&
              insights.length > 0 && (
                <div className="grid gap-4 md:grid-cols-2">
                  {insights.map((insight, i) => (
                    <InsightCard
                      key={i}
                      insight={insight}
                    />
                  ))}
                </div>
              )}
          </section>
        </div>
      )}
    </main>
  );
}

function TrendingUpIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      className="text-accent-pink"
    >
      <path d="M3 17l6-6 4 4 8-9" />
      <path d="M14 6h7v7" />
    </svg>
  );
}