"""
Generic paginated response wrapper. Every list endpoint returns this shape
so the frontend has one pagination UI pattern instead of five slightly
different ones.
"""
import math
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def build(cls, items: list[T], total: int, page: int, page_size: int) -> "Page[T]":
        total_pages = math.ceil(total / page_size) if page_size else 0
        return cls(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)
