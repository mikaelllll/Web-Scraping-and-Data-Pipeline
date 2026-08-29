export type Run = { id: string; status: 'queued' | 'running' | 'completed' | 'failed'; started_at: string; finished_at: string | null; collected: number; inserted: number; duplicates: number; failures: number; error: string | null }
export type Story = { id: string; title: string; topic: string; trend_score: number; source_count: number; article_count: number; first_seen_at: string; last_seen_at: string }
export type Article = { id: string; title: string; canonical_url: string; author: string | null; excerpt: string | null; published_at: string; categories: string[]; source_name: string }
export type Dashboard = { metrics: { sources: number; articles: number; stories: number; latest_run_status: string }; stories: Story[]; articles: Article[]; latest_run: Run | null }

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json', ...options?.headers } })
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Unexpected service error' }))
    throw new Error(body.detail ?? `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const api = {
  dashboard: () => request<Dashboard>('/api/v1/dashboard'),
  startRun: () => request<Run>('/api/v1/runs', { method: 'POST' }),
  run: (id: string) => request<Run>(`/api/v1/runs/${id}`),
}

