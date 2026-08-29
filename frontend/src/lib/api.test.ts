import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from './api'

describe('API client', () => {
  afterEach(() => vi.restoreAllMocks())

  it('requests a new collection run with POST', async () => {
    const response = { id: 'run-1', status: 'queued' }
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(response), {
        status: 202,
        headers: { 'Content-Type': 'application/json' },
      }),
    )

    await expect(api.startRun()).resolves.toMatchObject(response)
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/runs',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('surfaces the API error detail', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'A collection run is already active' }), {
        status: 409,
        headers: { 'Content-Type': 'application/json' },
      }),
    )

    await expect(api.startRun()).rejects.toThrow('A collection run is already active')
  })
})
