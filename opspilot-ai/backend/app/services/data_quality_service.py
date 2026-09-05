"""
Data quality engine.

Computes a quality report for an uploaded DataFrame: missing values,
duplicate rows, and outliers on numeric columns (IQR method — no need for
Isolation Forest at ingestion time; that's reserved for the dedicated
anomaly-detection engine in Phase 6, which looks for anomalies in business
metrics over time, not bad rows in an upload).

The report shape is what gets stored in Dataset.quality_report and shown
in the UI as e.g. "Data Quality: 94% — 14 duplicate rows, 31 missing values,
3 potential outliers."
"""
from typing import Any

import pandas as pd


def _count_outliers_iqr(series: pd.Series) -> int:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric) < 4:
        return 0
    q1, q3 = numeric.quantile(0.25), numeric.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return int(((numeric < lower) | (numeric > upper)).sum())


def generate_quality_report(
    df: pd.DataFrame,
    required_columns: list[str],
    numeric_columns: list[str],
) -> dict[str, Any]:
    total_rows = len(df)

    missing_by_column = {
        col: int(df[col].isna().sum()) for col in required_columns if col in df.columns
    }
    total_missing = sum(missing_by_column.values())

    duplicate_rows = int(df.duplicated().sum())

    # A row is "invalid" if it's missing any required field — the same rows
    # get dropped during cleaning, so this count is what the user sees
    # reflected in "valid records" below.
    if required_columns:
        invalid_mask = df[required_columns].isna().any(axis=1)
        invalid_rows = int(invalid_mask.sum())
    else:
        invalid_rows = 0

    outliers_by_column = {
        col: _count_outliers_iqr(df[col]) for col in numeric_columns if col in df.columns
    }
    total_outliers = sum(outliers_by_column.values())

    valid_rows = total_rows - invalid_rows
    valid_percentage = round((valid_rows / total_rows) * 100, 1) if total_rows else 0.0

    # Overall score weights validity most heavily, with duplicates and
    # outliers as smaller deductions — meant to be a quick at-a-glance
    # signal, not a rigorous statistical measure.
    duplicate_penalty = min(10.0, (duplicate_rows / total_rows) * 100) if total_rows else 0.0
    outlier_penalty = min(5.0, (total_outliers / total_rows) * 100) if total_rows else 0.0
    quality_score = round(max(0.0, valid_percentage - duplicate_penalty - outlier_penalty), 1)

    return {
        "quality_score": quality_score,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "valid_percentage": valid_percentage,
        "duplicate_rows": duplicate_rows,
        "missing_values": {
            "total": total_missing,
            "by_column": missing_by_column,
        },
        "outliers": {
            "total": total_outliers,
            "by_column": outliers_by_column,
        },
    }
