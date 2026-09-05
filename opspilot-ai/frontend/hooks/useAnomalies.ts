"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { AnomaliesResponse, Anomaly } from "@/types/ml";

export function useAnomalies() {
  const { activeOrgId } = useAuth();
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    apiFetch<AnomaliesResponse>("/anomalies")
      .then((r) => setAnomalies(r.anomalies))
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  return { anomalies, isLoading };
}
