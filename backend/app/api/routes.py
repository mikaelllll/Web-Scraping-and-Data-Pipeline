import uuid
from datetime import UTC, datetime

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session
from app.models import CollectionRun, Source
from app.schemas import RunOut, SourceCreate
from app.services.pipeline import dashboard_snapshot

router = APIRouter(prefix="/api/v1")


@router.get("/dashboard")
async def dashboard(session: AsyncSession = Depends(get_session)) -> dict:
    return await dashboard_snapshot(session)


@router.post("/runs", response_model=RunOut, status_code=status.HTTP_202_ACCEPTED)
async def start_run(session: AsyncSession = Depends(get_session)) -> CollectionRun:
    active = await session.scalar(
        select(CollectionRun).where(CollectionRun.status.in_(["queued", "running"])).limit(1)
    )
    if active:
        raise HTTPException(status_code=409, detail="A collection run is already active")
    run = CollectionRun(status="queued", started_at=datetime.now(UTC))
    session.add(run)
    await session.commit()
    await session.refresh(run)
    redis = await create_pool(RedisSettings.from_dsn(get_settings().redis_url))
    await redis.enqueue_job("collect_news", str(run.id))
    await redis.close()
    return run


@router.get("/runs/{run_id}", response_model=RunOut)
async def get_run(run_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> CollectionRun:
    run = await session.get(CollectionRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Collection run not found")
    return run


@router.post("/sources", status_code=status.HTTP_201_CREATED)
async def add_source(payload: SourceCreate, session: AsyncSession = Depends(get_session)) -> dict:
    if await session.scalar(select(Source.id).where(Source.name == payload.name)):
        raise HTTPException(status_code=409, detail="Source name already exists")
    source = Source(name=payload.name.strip(), feed_url=str(payload.feed_url))
    session.add(source)
    await session.commit()
    return {"id": source.id, "name": source.name, "feed_url": source.feed_url}
