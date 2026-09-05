"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { ChurnRisk } from "@/types/ml";

export function useChurn() {
  const { activeOrgId } = useAuth();
  const [churn, setChurn] = useState<ChurnRisk | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    setError(null);
    apiFetch<ChurnRisk>("/customers/churn-risk")
      .then(setChurn)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load churn data."))
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  return { churn, error, isLoading };
}
