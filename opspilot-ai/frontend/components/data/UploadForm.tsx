"use client";

import { useRef, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import { Button } from "@/components/common/Button";
import type { Dataset, DatasetType } from "@/types/dataset";

const DATASET_TYPES: { value: DatasetType; label: string }[] = [
  { value: "sales", label: "Sales" },
  { value: "customers", label: "Customers" },
  { value: "products", label: "Products" },
  { value: "inventory", label: "Inventory" },
  { value: "expenses", label: "Expenses" },
];

export function UploadForm({ onUploaded }: { onUploaded: (dataset: Dataset) => void }) {
  const [datasetType, setDatasetType] = useState<DatasetType>("sales");
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function pickFile(f: File | undefined) {
    if (!f) return;
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (!["csv", "xlsx", "xls"].includes(ext ?? "")) {
      setError("Only .csv, .xlsx, and .xls files are supported.");
      return;
    }
    setError(null);
    setFile(f);
  }

  async function handleUpload() {
    if (!file) return;
    setIsUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("dataset_type", datasetType);

      const dataset = await apiFetch<Dataset>("/datasets/upload", {
        method: "POST",
        body: formData,
      });
      onUploaded(dataset);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed. Try again.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div className="rounded-card border border-border bg-background-card p-5">
      <p className="text-sm font-medium text-text-muted">Upload a dataset</p>

      <div className="mt-3 flex gap-2">
        {DATASET_TYPES.map((t) => (
          <button
            key={t.value}
            onClick={() => setDatasetType(t.value)}
            className={`rounded-full border px-3 py-1 text-xs transition-colors ${
              datasetType === t.value
                ? "border-accent-indigo bg-accent-indigo/10 text-text-primary"
                : "border-border text-text-muted hover:border-accent-indigo/50"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          pickFile(e.dataTransfer.files?.[0]);
        }}
        onClick={() => inputRef.current?.click()}
        className={`mt-4 flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed px-4 py-8 text-center transition-colors ${
          isDragging ? "border-accent-indigo bg-accent-indigo/5" : "border-border"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={(e) => pickFile(e.target.files?.[0])}
        />
        {file ? (
          <p className="text-sm">{file.name}</p>
        ) : (
          <>
            <p className="text-sm text-text-primary">Drag & drop a file here</p>
            <p className="mt-1 text-xs text-text-muted">or click to browse — .csv, .xlsx, .xls</p>
          </>
        )}
      </div>

      {error && <p className="mt-2 text-sm text-status-danger">{error}</p>}

      <div className="mt-4">
        <Button onClick={handleUpload} loading={isUploading} disabled={!file}>
          Upload {DATASET_TYPES.find((t) => t.value === datasetType)?.label} data
        </Button>
      </div>
    </div>
  );
}
