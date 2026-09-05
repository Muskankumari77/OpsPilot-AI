export interface KBDocument {
  id: number;
  filename: string;
  created_at: string;
  chunk_count: number;
}

export interface Action {
  id: number;
  title: string;
  description: string | null;
  priority: "low" | "medium" | "high";
  status: "pending" | "in_progress" | "completed" | "cancelled";
  owner: string | null;
  due_date: string | null;
  related_product_id: number | null;
  related_customer_id: number | null;
  created_at: string;
}

export interface AlertItem {
  id: number;
  type: "critical" | "warning" | "information" | "success";
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface InsightCard {
  severity: string;
  title: string;
  explanation: string;
  supporting_metric: string;
  recommendation: string;
}

export interface ReportSection {
  heading: string;
  content: string;
}

export interface Report {
  title: string;
  generated_at: string;
  sections: ReportSection[];
}
