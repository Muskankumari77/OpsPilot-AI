"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { Action } from "@/types/operations";

export function useActions() {
  const { activeOrgId } = useAuth();
  const [actions, setActions] = useState<Action[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    apiFetch<Action[]>("/actions")
      .then(setActions)
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function updateStatus(actionId: number, status: Action["status"]) {
    const updated = await apiFetch<Action>(`/actions/${actionId}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    setActions((prev) => prev.map((a) => (a.id === actionId ? updated : a)));
  }

  return { actions, isLoading, updateStatus, refresh };
}
