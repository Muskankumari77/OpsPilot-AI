from datetime import datetime

from pydantic import BaseModel


class ReportSection(BaseModel):
    heading: str
    content: str


class ReportOut(BaseModel):
    title: str
    generated_at: datetime
    sections: list[ReportSection]
