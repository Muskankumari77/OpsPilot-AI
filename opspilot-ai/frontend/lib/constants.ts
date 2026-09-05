/**
 * Kept as plain constants rather than fetched from the API — matches the
 * fixed lists in backend/scripts/generate_demo_data.py. If a real
 * organization uploads data with different categories/regions, these
 * filter dropdowns simply won't include the new values; a future
 * improvement would fetch distinct values from the backend instead.
 */
export const PRODUCT_CATEGORIES = [
  "Electronics",
  "Home & Kitchen",
  "Apparel",
  "Beauty",
  "Sports",
  "Office Supplies",
  "Toys",
];

export const REGIONS = ["North", "South", "East", "West", "Central"];

export const EXPENSE_CATEGORIES = [
  "rent",
  "salaries",
  "marketing",
  "shipping",
  "suppliers",
  "operations",
  "misc",
];
