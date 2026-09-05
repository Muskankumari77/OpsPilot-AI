"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface BreakdownChartProps {
  data: { label: string; value: number }[];
  valuePrefix?: string;
}

export function BreakdownChart({ data, valuePrefix = "$" }: BreakdownChartProps) {
  if (data.length === 0) {
    return <p className="text-sm text-text-muted">No data in this period yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1E2A3E" horizontal={false} />
        <XAxis type="number" stroke="#94A3B8" fontSize={12} tickLine={false} />
        <YAxis type="category" dataKey="label" stroke="#94A3B8" fontSize={12} width={110} tickLine={false} />
        <Tooltip
          contentStyle={{ background: "#101A2C", border: "1px solid #1E2A3E", borderRadius: 8 }}
          labelStyle={{ color: "#F5F7FA" }}
          formatter={(value: number) => [`${valuePrefix}${value.toLocaleString()}`, "Value"]}
        />
        <Bar dataKey="value" fill="#22D3EE" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
