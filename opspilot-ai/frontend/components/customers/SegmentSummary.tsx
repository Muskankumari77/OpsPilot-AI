import type { SegmentationResult } from "@/types/ml";
import { Button } from "@/components/common/Button";

const SEGMENT_COLORS: Record<string, string> = {
  VIP: "bg-accent-violet/15 text-accent-violet",
  Loyal: "bg-status-success/15 text-status-success",
  New: "bg-accent-cyan/10 text-accent-cyan",
  "At Risk": "bg-status-danger/15 text-status-danger",
};

export function SegmentSummary({
  segments,
  isRunning,
  onRun,
}: {
  segments: SegmentationResult | null;
  isRunning: boolean;
  onRun: () => void;
}) {
  const hasSegments = segments && segments.customers_segmented > 0;

  return (
    <div className="rounded-card border border-border bg-background-card p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-text-muted">Customer Segments (RFM + K-Means)</p>
        <Button onClick={onRun} loading={isRunning} className="w-auto px-4 py-1.5 text-xs">
          {hasSegments ? "Re-run segmentation" : "Run segmentation"}
        </Button>
      </div>

      {!hasSegments && !isRunning && (
        <p className="mt-3 text-sm text-text-muted">
          No segments computed yet — click &quot;Run segmentation&quot; to cluster
          customers by recency, frequency, and monetary value.
        </p>
      )}

      {hasSegments && (
        <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {segments!.by_segment.map((s) => (
            <div key={s.segment} className="rounded-lg border border-border p-3 text-center">
              <p className="font-display text-xl font-semibold">{s.count}</p>
              <span className={`mt-1 inline-block rounded-full px-2 py-0.5 text-xs ${SEGMENT_COLORS[s.segment] ?? ""}`}>
                {s.segment}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
