"use client";

import { useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import { Button } from "@/components/common/Button";
import type { Report } from "@/types/operations";

function reportToMarkdown(report: Report): string {
  const lines = [`# ${report.title}`, `_Generated ${new Date(report.generated_at).toLocaleString()}_`, ""];
  for (const section of report.sections) {
    lines.push(`## ${section.heading}`, section.content, "");
  }
  return lines.join("\n");
}

function downloadMarkdown(report: Report) {
  const blob = new Blob([reportToMarkdown(report)], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${report.title.replace(/\s+/g, "-").toLowerCase()}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ReportsPage() {
  const [reportType, setReportType] = useState<"daily" | "weekly" | "monthly">("monthly");
  const [report, setReport] = useState<Report | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setIsGenerating(true);
    setError(null);
    try {
      const result = await apiFetch<Report>(`/reports/generate?report_type=${reportType}`, { method: "POST" });
      setReport(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't generate the report.");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <main className="px-6 py-8">
      <h1 className="font-display text-2xl font-semibold">Reports</h1>
      <p className="mt-1 text-sm text-text-muted">
        A compiled business report covering sales, inventory, customers, expenses,
        forecast, and recommendations.
      </p>

      <div className="mt-5 flex items-center gap-3">
        <select
          value={reportType}
          onChange={(e) => setReportType(e.target.value as typeof reportType)}
          className="rounded-lg border border-border bg-background-surface px-3 py-2 text-sm outline-none focus:border-accent-indigo"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
        <Button onClick={handleGenerate} loading={isGenerating} className="w-auto px-5">
          Generate report
        </Button>
        {report && (
          <button
            onClick={() => downloadMarkdown(report)}
            className="text-sm text-accent-cyan hover:underline"
          >
            Download as Markdown
          </button>
        )}
      </div>

      {error && <p className="mt-4 text-sm text-status-danger">{error}</p>}

      {report && (
        <div className="mt-6 rounded-card border border-border bg-background-card p-6">
          <h2 className="font-display text-xl font-semibold">{report.title}</h2>
          <p className="mt-1 text-xs text-text-muted">
            Generated {new Date(report.generated_at).toLocaleString()}
          </p>
          <div className="mt-5 space-y-5">
            {report.sections.map((section) => (
              <div key={section.heading}>
                <p className="text-sm font-medium text-accent-cyan">{section.heading}</p>
                <p className="mt-1 whitespace-pre-wrap text-sm text-text-muted">{section.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
