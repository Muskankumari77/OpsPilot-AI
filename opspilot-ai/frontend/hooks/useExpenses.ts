"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { ExpenseItem, ExpenseSummary, Page } from "@/types/analytics";

export function useExpenses() {
  const { activeOrgId } = useAuth();
  const [summary, setSummary] = useState<ExpenseSummary | null>(null);
  const [items, setItems] = useState<ExpenseItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!activeOrgId) return;
    setIsLoading(true);

    Promise.all([
      apiFetch<ExpenseSummary>("/expenses/summary"),
      apiFetch<Page<ExpenseItem>>("/expenses?page_size=50"),
    ])
      .then(([s, p]) => {
        setSummary(s);
        setItems(p.items);
      })
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  return { summary, items, isLoading };
}
