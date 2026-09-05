"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { DashboardSummary } from "@/types/analytics";

export function useDashboard() {
  const { activeOrgId } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    apiFetch<DashboardSummary>("/dashboard/summary")
      .then(setSummary)
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  return { summary, isLoading };
}
