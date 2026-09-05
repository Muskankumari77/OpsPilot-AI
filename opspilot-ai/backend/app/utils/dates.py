"""
Date range helpers shared by every "summary" endpoint (sales, expenses,
dashboard) so "current period vs previous period" comparisons are computed
the same way everywhere instead of each service reinventing the math.
"""
from datetime import date, timedelta
from typing import Optional


def resolve_period(
    date_from: Optional[date],
    date_to: Optional[date],
    default_days: int = 30,
) -> tuple[date, date, date, date]:
    """
    Returns (start, end, prev_start, prev_end).

    If no dates are given, defaults to the trailing `default_days` days vs
    the equal-length period immediately before it. If the caller supplies
    an explicit range, the "previous period" is the same-length window
    immediately preceding it — this is what powers every "X% vs last
    period" figure in the dashboards.
    """
    if date_to is None:
        date_to = date.today()
    if date_from is None:
        date_from = date_to - timedelta(days=default_days - 1)

    period_length = (date_to - date_from).days + 1
    prev_end = date_from - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_length - 1)

    return date_from, date_to, prev_start, prev_end


def percent_change(current: float, previous: float) -> Optional[float]:
    """Returns None (rather than a misleading number) when there's no
    baseline to compare against."""
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 1)
