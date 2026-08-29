# Frontend

The React and TypeScript dashboard is designed as an operational view, not a static landing page. It polls only while a run remains active, stops automatically after terminal status, refreshes results on completion, reports partial source failures, and links all articles to their publishers.

Refreshing the browser during a collection does not lose progress tracking: the persisted latest run is restored from the dashboard response and polling resumes. “Refresh dashboard” performs a read only; “Collect latest news” creates actual pipeline work.

The responsive interface includes pipeline metrics, ranked story clusters, explainable trend context, recent coverage search, job feedback, an architecture overview, and a direct link to OpenAPI documentation. Nginx serves the production build and proxies API requests, avoiding environment-specific frontend URLs.
