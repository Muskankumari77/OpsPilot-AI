"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { InsightCard } from "@/types/operations";

export function useInsights() {
  const { activeOrgId } = useAuth();
  const [insights, setInsights] = useState<InsightCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    apiFetch<InsightCard[]>("/insights")
      .then(setInsights)
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  return { insights, isLoading };
}
