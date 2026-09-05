import type { SalesFilters } from "@/hooks/useSales";

interface SalesFilterBarProps {
  filters: SalesFilters;
  onChange: (filters: SalesFilters) => void;
  regions: string[];
  categories: string[];
}

export function SalesFilterBar({ filters, onChange, regions, categories }: SalesFilterBarProps) {
  return (
    <div className="flex flex-wrap gap-3">
      <select
        value={filters.region ?? ""}
        onChange={(e) => onChange({ ...filters, region: e.target.value || undefined })}
        className="rounded-lg border border-border bg-background-surface px-3 py-2 text-sm outline-none focus:border-accent-indigo"
      >
        <option value="">All regions</option>
        {regions.map((r) => (
          <option key={r} value={r}>
            {r}
          </option>
        ))}
      </select>

      <select
        value={filters.category ?? ""}
        onChange={(e) => onChange({ ...filters, category: e.target.value || undefined })}
        className="rounded-lg border border-border bg-background-surface px-3 py-2 text-sm outline-none focus:border-accent-indigo"
      >
        <option value="">All categories</option>
        {categories.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <input
        type="date"
        value={filters.dateFrom ?? ""}
        onChange={(e) => onChange({ ...filters, dateFrom: e.target.value || undefined })}
        className="rounded-lg border border-border bg-background-surface px-3 py-2 text-sm outline-none focus:border-accent-indigo"
      />
      <input
        type="date"
        value={filters.dateTo ?? ""}
        onChange={(e) => onChange({ ...filters, dateTo: e.target.value || undefined })}
        className="rounded-lg border border-border bg-background-surface px-3 py-2 text-sm outline-none focus:border-accent-indigo"
      />
    </div>
  );
}
