import ipaddress
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


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
    name: str = Field(min_length=2, max_length=80)
    feed_url: HttpUrl

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Source name must contain at least two visible characters")
        return normalized

    @field_validator("feed_url")
    @classmethod
    def reject_local_feed_urls(cls, value: HttpUrl) -> HttpUrl:
        host = (value.host or "").lower()
        if host == "localhost" or host.endswith(".localhost"):
            raise ValueError("Local feed URLs are not allowed")
        try:
            address = ipaddress.ip_address(host.strip("[]"))
        except ValueError:
            return value
        if not address.is_global:
            raise ValueError("Private or reserved feed addresses are not allowed")
        return value


class SourceOut(BaseModel):
    id: int
    name: str
    feed_url: str


class DashboardMetrics(BaseModel):
    sources: int
    articles: int
    stories: int
    latest_run_status: str


class DashboardOut(BaseModel):
    metrics: DashboardMetrics
    stories: list[StoryOut]
    articles: list[ArticleOut]
    latest_run: RunOut | None
