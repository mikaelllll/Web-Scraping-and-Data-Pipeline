# Testing and engineering decisions

CI runs on pushes, pull requests, and manual dispatch. It performs Ruff static analysis, backend unit tests, a strict TypeScript production build, Compose configuration validation, and complete container builds.

Unit tests cover URL idempotency, HTML cleanup, RSS parsing, similarity behavior, topic inference, and trend decay. Integration and browser tests are natural next layers if the project becomes a deployed product.

## Deliberate trade-offs

- **RSS/Atom first:** more stable and responsible than scraping arbitrary pages.
- **Deterministic clustering:** transparent and free for a Codespaces demonstration.
- **Polling only during active runs:** simple, robust feedback without permanent traffic.
- **Database constraints:** idempotency does not rely only on application timing.
- **Isolated workers:** slow or failed sources do not consume API request workers.
- **No authentication:** the Codespace is the security boundary for this public demonstration. Authentication and multi-tenancy would be required for a shared deployment.

