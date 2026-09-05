"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { CustomerItem, CustomerSummary, Page } from "@/types/analytics";

export function useCustomers() {
  const { activeOrgId } = useAuth();
  const [summary, setSummary] = useState<CustomerSummary | null>(null);
  const [items, setItems] = useState<CustomerItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);

    Promise.all([
      apiFetch<CustomerSummary>("/customers/summary"),
      apiFetch<Page<CustomerItem>>("/customers?page_size=50"),
    ])
      .then(([s, p]) => {
        setSummary(s);
        setItems(p.items);
      })
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  return { summary, items, isLoading };
}
