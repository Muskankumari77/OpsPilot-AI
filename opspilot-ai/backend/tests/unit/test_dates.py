from datetime import date

from app.utils.dates import percent_change, resolve_period


def test_resolve_period_defaults_to_trailing_30_days():
    start, end, prev_start, prev_end = resolve_period(None, None, default_days=30)
    assert (end - start).days == 29
    assert (prev_end - prev_start).days == 29
    assert prev_end < start


def test_resolve_period_explicit_range_matches_previous_window_length():
    start, end, prev_start, prev_end = resolve_period(date(2026, 8, 1), date(2026, 8, 10))
    assert (end - start).days == (prev_end - prev_start).days
    assert prev_end == date(2026, 7, 31)


def test_percent_change_basic():
    assert percent_change(110, 100) == 10.0
    assert percent_change(90, 100) == -10.0


def test_percent_change_no_baseline_returns_none():
    assert percent_change(50, 0) is None
