import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class RunStatus(StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    feed_url: Mapped[str] = mapped_column(String(500), unique=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    articles: Mapped[list["Article"]] = relationship(back_populates="source")


class Story(Base):
    __tablename__ = "stories"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    representative_title: Mapped[str] = mapped_column(String(500))
    topic: Mapped[str] = mapped_column(String(80), index=True)
    trend_score: Mapped[float] = mapped_column(Float, default=0)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    articles: Mapped[list["Article"]] = relationship(back_populates="story")


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (UniqueConstraint("canonical_url", name="uq_article_canonical_url"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    story_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("stories.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    canonical_url: Mapped[str] = mapped_column(String(1000))
    author: Mapped[str | None] = mapped_column(String(200))
    excerpt: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    categories: Mapped[list[str]] = mapped_column(JSONB, default=list)
    comment_count: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[Source] = relationship(back_populates="articles")
    story: Mapped[Story | None] = relationship(back_populates="articles")


class CollectionRun(Base):
    __tablename__ = "collection_runs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.queued)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected: Mapped[int] = mapped_column(Integer, default=0)
    inserted: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    failures: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
