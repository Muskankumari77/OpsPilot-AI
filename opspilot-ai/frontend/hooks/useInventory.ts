"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { InventoryItem, InventorySummary, Page } from "@/types/analytics";

export function useInventory(understockedOnly: boolean) {
  const { activeOrgId } = useAuth();
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    const qs = understockedOnly ? "?understocked_only=true&page_size=100" : "?page_size=100";

    Promise.all([
      apiFetch<InventorySummary>("/inventory/summary"),
      apiFetch<Page<InventoryItem>>(`/inventory${qs}`),
    ])
      .then(([s, p]) => {
        setSummary(s);
        setItems(p.items);
      })
      .finally(() => setIsLoading(false));
  }, [activeOrgId, understockedOnly]);

  return { summary, items, isLoading };
}
