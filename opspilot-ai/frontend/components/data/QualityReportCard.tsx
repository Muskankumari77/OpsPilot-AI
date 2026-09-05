import type { QualityReport } from "@/types/dataset";

function scoreColor(score: number) {
  if (score >= 90) return "text-status-success";
  if (score >= 70) return "text-status-warning";
  return "text-status-danger";
}

export function QualityReportCard({ report }: { report: QualityReport }) {
  return (
    <div className="mt-3 rounded-lg border border-border bg-background-surface p-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-text-muted">Data Quality</p>
        <p className={`text-lg font-semibold ${scoreColor(report.quality_score)}`}>
          {report.quality_score}%
        </p>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-text-muted sm:grid-cols-4">
        <p>{report.valid_percentage}% valid records</p>
        <p>{report.duplicate_rows} duplicate rows</p>
        <p>{report.missing_values.total} missing values</p>
        <p>{report.outliers.total} potential outliers</p>
      </div>
    </div>
  );
}
