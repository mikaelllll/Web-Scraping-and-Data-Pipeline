# Operations and troubleshooting

## Inspect services

```bash
docker compose ps
docker compose logs --tail=100 api worker frontend
```

## Print the Codespaces URL

```bash
bash .devcontainer/show-url.sh
```

If the page is not ready, confirm that `frontend`, `api`, `postgres`, and `redis` are healthy. The worker does not expose an HTTP health endpoint; its ARQ health output appears in its logs.

## Rebuild after code changes

```bash
docker compose up --build --detach
```

## Reset demonstration data

The following intentionally removes local container data:

```bash
docker compose down --volumes
docker compose up --build --detach
```

Never use the reset command if the local database contains information you intend to preserve.

