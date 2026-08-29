import uuid

from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.pipeline import execute_collection


async def collect_news(_context: dict, run_id: str) -> None:
    async with SessionLocal() as session:
        await execute_collection(session, uuid.UUID(run_id))


class WorkerSettings:
    functions = [collect_news]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    max_jobs = 4
    job_timeout = 180
    max_tries = 3
    health_check_interval = 15
