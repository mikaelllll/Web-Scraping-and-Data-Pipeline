import uuid
from datetime import UTC, datetime

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session
from app.models import CollectionRun, RunStatus, Source
from app.schemas import DashboardOut, RunOut, SourceCreate, SourceOut
from app.services.pipeline import dashboard_snapshot

router = APIRouter(prefix="/api/v1")


COLLECTION_LOCK_KEY = 734_251_901


@router.get("/dashboard", response_model=DashboardOut)
async def dashboard(session: AsyncSession = Depends(get_session)) -> dict:
    return await dashboard_snapshot(session)


@router.post("/runs", response_model=RunOut, status_code=status.HTTP_202_ACCEPTED)
async def start_run(session: AsyncSession = Depends(get_session)) -> CollectionRun:
    # Serializes the check-and-create transaction across all API replicas.
    await session.execute(
        text("SELECT pg_advisory_xact_lock(:key)"), {"key": COLLECTION_LOCK_KEY}
    )
    active = await session.scalar(
        select(CollectionRun)
        .where(CollectionRun.status.in_([RunStatus.queued, RunStatus.running]))
        .limit(1)
    )
    if active:
        raise HTTPException(status_code=409, detail="A collection run is already active")
    run = CollectionRun(status=RunStatus.queued, started_at=datetime.now(UTC))
    session.add(run)
    await session.commit()
    await session.refresh(run)
    redis = None
    try:
        redis = await create_pool(RedisSettings.from_dsn(get_settings().redis_url))
        job = await redis.enqueue_job("collect_news", str(run.id), _job_id=f"collection:{run.id}")
        if job is None:
            raise RuntimeError("The collection job could not be queued")
    except Exception:
        run.status = RunStatus.failed
        run.finished_at = datetime.now(UTC)
        run.error = "The worker queue was unavailable when the run was created"
        await session.commit()
        raise HTTPException(status_code=503, detail="The worker queue is unavailable") from None
    finally:
        if redis is not None:
            await redis.aclose()
    return run


@router.get("/runs/{run_id}", response_model=RunOut)
async def get_run(run_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> CollectionRun:
    run = await session.get(CollectionRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Collection run not found")
    return run


@router.post("/sources", response_model=SourceOut, status_code=status.HTTP_201_CREATED)
async def add_source(payload: SourceCreate, session: AsyncSession = Depends(get_session)) -> dict:
    name = payload.name.strip()
    if await session.scalar(select(Source.id).where(Source.name == name)):
        raise HTTPException(status_code=409, detail="Source name already exists")
    source = Source(name=name, feed_url=str(payload.feed_url))
    session.add(source)
    await session.commit()
    return {"id": source.id, "name": source.name, "feed_url": source.feed_url}
