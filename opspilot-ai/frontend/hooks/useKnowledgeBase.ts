"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { KBDocument } from "@/types/operations";

export function useKnowledgeBase() {
  const { activeOrgId } = useAuth();
  const [documents, setDocuments] = useState<KBDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(() => {
    if (!activeOrgId) return;
    setIsLoading(true);
    apiFetch<KBDocument[]>("/knowledge-base/documents")
      .then(setDocuments)
      .finally(() => setIsLoading(false));
  }, [activeOrgId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function uploadDocument(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const doc = await apiFetch<KBDocument>("/knowledge-base/upload", { method: "POST", body: formData });
    setDocuments((prev) => [doc, ...prev]);
  }

  return { documents, isLoading, uploadDocument, refresh };
}
