export interface DashboardKPI {
  value: number;
  growth_pct: number | null;
}

export interface DashboardSummary {
  business_health_score: number;
  revenue: DashboardKPI;
  orders: DashboardKPI;
  profit: DashboardKPI;
  profit_margin_pct: number;
  total_customers: number;
  new_customers_this_month: number;
  understocked_products: number;
  total_products: number;
}

export interface SalesSummary {
  total_revenue: number;
  revenue_growth_pct: number | null;
  total_orders: number;
  orders_growth_pct: number | null;
  average_order_value: number;
  gross_profit: number;
  profit_margin_pct: number;
  units_sold: number;
  period_start: string;
  period_end: string;
}

export interface TimeSeriesPoint {
  period: string;
  value: number;
}

export interface CategoryBreakdown {
  category: string;
  revenue: number;
}

export interface RegionBreakdown {
  region: string;
  revenue: number;
}

export interface ProductPerformance {
  product_id: number;
  product_name: string;
  revenue: number;
  units_sold: number;
}

export interface SalesTrends {
  revenue_over_time: TimeSeriesPoint[];
  orders_over_time: TimeSeriesPoint[];
  revenue_by_category: CategoryBreakdown[];
  revenue_by_region: RegionBreakdown[];
  top_products: ProductPerformance[];
  worst_products: ProductPerformance[];
}

export interface RiskLevelCount {
  risk_level: string;
  count: number;
}

export interface InventorySummary {
  total_products: number;
  total_inventory_value: number;
  by_risk_level: RiskLevelCount[];
}

export interface InventoryItem {
  id: number;
  product_id: number;
  current_stock: number;
  reorder_point: number;
  updated_at: string;
  product_sku: string;
  product_name: string;
  category: string;
  is_understocked: boolean;
  risk_level: string;
}

export interface RegionCount {
  region: string;
  count: number;
}

export interface CustomerSummary {
  total_customers: number;
  new_customers_this_month: number;
  by_region: RegionCount[];
}

export interface CustomerItem {
  id: number;
  name: string;
  email: string;
  region: string;
  segment: string | null;
  created_at: string;
}

export interface ExpenseCategoryBreakdown {
  category: string;
  amount: number;
}

export interface ExpenseTrendPoint {
  period: string;
  amount: number;
}

export interface ExpenseSummary {
  total_expenses: number;
  month_over_month_change_pct: number | null;
  by_category: ExpenseCategoryBreakdown[];
  trend: ExpenseTrendPoint[];
  period_start: string;
  period_end: string;
}

export interface ExpenseItem {
  id: number;
  category: string;
  amount: number;
  expense_date: string;
  description: string | null;
  created_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
