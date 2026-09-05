"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { SegmentationResult } from "@/types/ml";

export function useSegments() {
  const { activeOrgId } = useAuth();
  const [segments, setSegments] = useState<SegmentationResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  const refresh = useCallback(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    apiFetch<SegmentationResult>("/customers/segments")
      .then(setSegments)
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function runSegmentation() {
    setIsRunning(true);
    try {
      const result = await apiFetch<SegmentationResult>("/customers/segment", { method: "POST" });
      setSegments(result);
    } finally {
      setIsRunning(false);
    }
  }

  return { segments, isLoading, isRunning, runSegmentation };
}
