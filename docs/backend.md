# Backend and API

The API uses FastAPI, Pydantic and SQLAlchemy's asynchronous engine. Configuration is loaded from environment variables with safe development defaults; credentials are not committed.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Container health probe |
| `GET` | `/ready` | PostgreSQL and Redis readiness probe |
| `GET` | `/api/v1/dashboard` | Aggregated metrics, trends and recent coverage |
| `POST` | `/api/v1/runs` | Queue a collection run |
| `GET` | `/api/v1/runs/{id}` | Inspect run progress and outcome |
| `POST` | `/api/v1/sources` | Register an RSS/Atom source |
| `GET` | `/api/docs` | Interactive OpenAPI documentation |

A second run is rejected with HTTP `409` while another is queued or running. This keeps the portfolio environment predictable and prevents accidental source bursts.

All dashboard and mutation responses use declared Pydantic models, keeping generated OpenAPI documentation synchronized with the actual payloads. Source names have explicit length validation, feed URLs require HTTP(S), database uniqueness constraints protect source identity, and internal queue errors are not exposed to clients.
