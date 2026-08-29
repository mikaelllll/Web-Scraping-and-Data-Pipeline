from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    canonical_url: str
    author: str | None
    excerpt: str | None
    published_at: datetime
    categories: list[str]
    source_name: str


class StoryOut(BaseModel):
    id: UUID
    title: str
    topic: str
    trend_score: float
    source_count: int
    article_count: int
    first_seen_at: datetime
    last_seen_at: datetime


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str
    started_at: datetime
    finished_at: datetime | None
    collected: int
    inserted: int
    duplicates: int
    failures: int
    error: str | None


class SourceCreate(BaseModel):
    name: str
    feed_url: HttpUrl
