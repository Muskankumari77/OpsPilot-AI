export type DatasetType = "sales" | "customers" | "products" | "inventory" | "expenses";
export type DatasetStatus = "processing" | "completed" | "failed";

export interface QualityReport {
  quality_score: number;
  total_rows: number;
  valid_rows: number;
  valid_percentage: number;
  duplicate_rows: number;
  missing_values: {
    total: number;
    by_column: Record<string, number>;
  };
  outliers: {
    total: number;
    by_column: Record<string, number>;
  };
}

export interface Dataset {
  id: number;
  filename: string;
  dataset_type: DatasetType;
  status: DatasetStatus;
  row_count: number | null;
  quality_report: QualityReport | null;
  error_message: string | null;
  created_at: string;
}

export interface DatasetSummary {
  products: number;
  customers: number;
  sales: number;
  inventory: number;
  expenses: number;
}
