# Architecture and data flow

NewsPulse separates request handling from collection. `POST /api/v1/runs` persists a queued run before publishing its identifier to Redis. An ARQ worker then owns network I/O, normalization, deduplication, clustering, scoring, and persistence. This keeps the API responsive and makes worker concurrency independently scalable.

PostgreSQL is the system of record. Redis is a delivery mechanism, not permanent business storage. A canonical-URL constraint provides final idempotency protection even if a job is retried.

A PostgreSQL transaction-level advisory lock makes run creation atomic across API replicas. This prevents two simultaneous requests from both passing the active-run check. Queue publication failures are converted into explicit failed runs and HTTP `503` responses.

## Services

- **frontend:** immutable React build served by Nginx; proxies `/api` to FastAPI.
- **api:** validates requests and exposes read models.
- **worker:** consumes queued collection jobs independently from the API.
- **redis:** queue broker with append-only persistence enabled.
- **postgres:** durable relational data and uniqueness constraints.

Horizontal scaling is possible by starting more worker replicas. Per-source concurrency controls and distributed collection locks would be the next additions before operating at internet scale.

The `/health` endpoint reports process liveness. `/ready` verifies both PostgreSQL and Redis, and container orchestration uses readiness before starting dependent services.
