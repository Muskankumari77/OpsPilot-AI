from pydantic import BaseModel


class SegmentCount(BaseModel):
    segment: str
    count: int


class SegmentationResultOut(BaseModel):
    customers_segmented: int
    by_segment: list[SegmentCount]
