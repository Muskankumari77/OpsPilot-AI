"use client";

import { useRef, useState } from "react";
import { useKnowledgeBase } from "@/hooks/useKnowledgeBase";
import { Button } from "@/components/common/Button";
import { ApiError } from "@/lib/api";

export default function KnowledgeBasePage() {
  const { documents, isLoading, uploadDocument } = useKnowledgeBase();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setIsUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <main className="px-6 py-8">
      <h1 className="font-display text-2xl font-semibold">Knowledge Base</h1>
      <p className="mt-1 text-sm text-text-muted">
        Upload internal policy documents (.txt or .md) — Ask OpsPilot can search
        them and cite sources when answering policy questions.
      </p>

      <div className="mt-6 rounded-card border border-border bg-background-card p-5">
        <input
          ref={inputRef}
          type="file"
          accept=".txt,.md"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <Button onClick={() => inputRef.current?.click()} loading={isUploading} className="w-auto px-5">
          Upload document
        </Button>
        {error && <p className="mt-2 text-sm text-status-danger">{error}</p>}
      </div>

      <div className="mt-6">
        {isLoading && <p className="text-sm text-text-muted">Loading documents...</p>}
        {!isLoading && documents.length === 0 && (
          <p className="text-sm text-text-muted">No documents uploaded yet.</p>
        )}
        {!isLoading && documents.length > 0 && (
          <div className="space-y-2">
            {documents.map((d) => (
              <div key={d.id} className="flex items-center justify-between rounded-card border border-border bg-background-card p-4">
                <div>
                  <p className="text-sm font-medium">{d.filename}</p>
                  <p className="text-xs text-text-muted">
                    {d.chunk_count} chunks &middot; {new Date(d.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
