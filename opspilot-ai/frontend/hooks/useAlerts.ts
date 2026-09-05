"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { AlertItem } from "@/types/operations";

export function useAlerts() {
  const { activeOrgId } = useAuth();
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    apiFetch<AlertItem[]>("/alerts")
      .then(setAlerts)
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function markRead(alertId: number) {
    const updated = await apiFetch<AlertItem>(`/alerts/${alertId}/read`, { method: "PATCH" });
    setAlerts((prev) => prev.map((a) => (a.id === alertId ? updated : a)));
  }

  return { alerts, isLoading, markRead };
}
