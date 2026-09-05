"use client";

import { useState } from "react";
import { useForecast } from "@/hooks/useForecast";
import { ForecastChart } from "@/components/forecasts/ForecastChart";
import { KPICard } from "@/components/dashboard/KPICard";

export default function ForecastsPage() {
  const [periods, setPeriods] = useState(3);
  const { forecast, error, isLoading } = useForecast(periods);

  return (
    <main className="px-6 py-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Revenue Forecast</h1>
          <p className="mt-1 text-sm text-text-muted">
            Baseline and XGBoost models are backtested on recent history — whichever
            is more accurate is used for the forecast shown below.
          </p>
        </div>
        <select
          value={periods}
          onChange={(e) => setPeriods(Number(e.target.value))}
          className="rounded-lg border border-border bg-background-surface px-3 py-2 text-sm outline-none focus:border-accent-indigo"
        >
          <option value={3}>Next 3 months</option>
          <option value={6}>Next 6 months</option>
          <option value={12}>Next 12 months</option>
        </select>
      </div>

      {isLoading && <p className="mt-8 text-sm text-text-muted">Training and evaluating models...</p>}

      {error && (
        <p className="mt-8 rounded-lg border border-status-warning/30 bg-status-warning/10 p-4 text-sm text-status-warning">
          {error}
        </p>
      )}

      {!isLoading && forecast && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <KPICard label="Model Used" value={forecast.model_used === "xgboost" ? "XGBoost" : "Baseline"} accent />
            <KPICard label="MAE" value={`$${forecast.evaluation.mae.toLocaleString()}`} />
            <KPICard label="RMSE" value={`$${forecast.evaluation.rmse.toLocaleString()}`} />
            <KPICard label="MAPE" value={`${forecast.evaluation.mape}%`} />
          </div>

          <div className="rounded-card border border-border bg-background-card p-5">
            <p className="text-sm font-medium text-text-muted">
              Revenue History & Forecast (shaded band = confidence range)
            </p>
            <div className="mt-3">
              <ForecastChart data={forecast} />
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
