"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { SalesSummary, SalesTrends } from "@/types/analytics";

export interface SalesFilters {
  dateFrom?: string;
  dateTo?: string;
  region?: string;
  category?: string;
}

function buildQuery(filters: SalesFilters): string {
  const params = new URLSearchParams();
  if (filters.dateFrom) params.set("date_from", filters.dateFrom);
  if (filters.dateTo) params.set("date_to", filters.dateTo);
  if (filters.region) params.set("region", filters.region);
  if (filters.category) params.set("category", filters.category);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function useSales(filters: SalesFilters) {
  const { activeOrgId } = useAuth();
  const [summary, setSummary] = useState<SalesSummary | null>(null);
  const [trends, setTrends] = useState<SalesTrends | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    const qs = buildQuery(filters);

    Promise.all([
      apiFetch<SalesSummary>(`/sales/summary${qs}`),
      apiFetch<SalesTrends>(`/sales/trends${qs}`),
    ])
      .then(([s, t]) => {
        setSummary(s);
        setTrends(t);
      })
      .finally(() => setIsLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeOrgId, filters.dateFrom, filters.dateTo, filters.region, filters.category]);

  return { summary, trends, isLoading };
}
