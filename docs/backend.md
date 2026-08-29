# Backend and API

The API uses FastAPI, Pydantic and SQLAlchemy's asynchronous engine. Configuration is loaded from environment variables with safe development defaults; credentials are not committed.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Container health probe |
| `GET` | `/api/v1/dashboard` | Aggregated metrics, trends and recent coverage |
| `POST` | `/api/v1/runs` | Queue a collection run |
| `GET` | `/api/v1/runs/{id}` | Inspect run progress and outcome |
| `POST` | `/api/v1/sources` | Register an RSS/Atom source |
| `GET` | `/api/docs` | Interactive OpenAPI documentation |

A second run is rejected with HTTP `409` while another is queued or running. This keeps the portfolio environment predictable and prevents accidental source bursts.

