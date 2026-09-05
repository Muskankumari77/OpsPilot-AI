"use client";

import {
  Area,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RevenueForecast } from "@/types/ml";

export function ForecastChart({ data }: { data: RevenueForecast }) {
  const combined = [
    ...data.history.map((h) => ({ period: h.period, actual: h.revenue })),
    ...data.forecast.map((f) => ({
      period: f.period,
      forecast: f.value,
      lower_bound: f.lower_bound,
      upper_bound: f.upper_bound,
    })),
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={combined} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <XAxis dataKey="period" stroke="#94A3B8" fontSize={12} tickLine={false} />
        <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} width={60} />
        <Tooltip
          contentStyle={{ background: "#101A2C", border: "1px solid #1E2A3E", borderRadius: 8 }}
          labelStyle={{ color: "#F5F7FA" }}
          formatter={(value: number) => [`$${value?.toLocaleString?.() ?? value}`, ""]}
        />
        <Area dataKey="upper_bound" stroke="none" fill="#6366F1" fillOpacity={0.08} />
        <Area dataKey="lower_bound" stroke="none" fill="#07111F" fillOpacity={1} />
        <Line type="monotone" dataKey="actual" stroke="#22D3EE" strokeWidth={2} dot={false} name="Actual" />
        <Line
          type="monotone"
          dataKey="forecast"
          stroke="#6366F1"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
          name="Forecast"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
