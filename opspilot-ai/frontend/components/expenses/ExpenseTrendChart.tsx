"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ExpenseTrendPoint } from "@/types/analytics";

export function ExpenseTrendChart({ data }: { data: ExpenseTrendPoint[] }) {
  if (data.length === 0) {
    return <p className="text-sm text-text-muted">No expense data in this period yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <XAxis dataKey="period" stroke="#94A3B8" fontSize={12} tickLine={false} />
        <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} width={60} />
        <Tooltip
          contentStyle={{ background: "#101A2C", border: "1px solid #1E2A3E", borderRadius: 8 }}
          labelStyle={{ color: "#F5F7FA" }}
          formatter={(value: number) => [`$${value.toLocaleString()}`, "Expenses"]}
        />
        <Line type="monotone" dataKey="amount" stroke="#F59E0B" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
