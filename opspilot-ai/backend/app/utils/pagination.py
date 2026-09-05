"""
Pagination utilities shared by every domain's list endpoint (products,
customers, sales, inventory, expenses) so pagination behavior — and its
query params — stay identical across the whole API instead of each route
reinventing offset/limit math.
"""
from fastapi import Query
from sqlalchemy.orm import Query as SAQuery


class PageParams:
    """FastAPI dependency: `page_params: PageParams = Depends()` gives every
    list endpoint the same `?page=&page_size=` query params for free."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="1-indexed page number"),
        page_size: int = Query(20, ge=1, le=200, description="Items per page (max 200)"),
    ):
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def paginate(query: SAQuery, params: PageParams) -> tuple[list, int]:
    """Applies offset/limit to a SQLAlchemy query and returns (items, total_count)."""
    total = query.count()
    items = query.offset(params.offset).limit(params.page_size).all()
    return items, total
