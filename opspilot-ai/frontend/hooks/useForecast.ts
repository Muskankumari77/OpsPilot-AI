"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { RevenueForecast } from "@/types/ml";

export function useForecast(periods: number) {
  const { activeOrgId } = useAuth();
  const [forecast, setForecast] = useState<RevenueForecast | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    setError(null);
    apiFetch<RevenueForecast>(`/forecasts/revenue?periods=${periods}`)
      .then(setForecast)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load the forecast."))
      .finally(() => setIsLoading(false));
  }, [activeOrgId, periods]);

  return { forecast, error, isLoading };
}
