import { describe, it, expect, vi, beforeEach } from 'vitest'
import { KeyValueClient } from '../src/client'

// Mock fetch
const createMockFetch = (response: any, status = 200) => {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => response,
  })
}

describe('KeyValueClient', () => {
  describe('constructor', () => {
    it('should use default base URL', () => {
      const client = new KeyValueClient()
      expect(client.getToken()).toBeUndefined()
    })

    it('should accept custom base URL', () => {
      const client = new KeyValueClient({ baseUrl: 'https://custom.com' })
      expect(client).toBeDefined()
    })

    it('should set default token', () => {
      const client = new KeyValueClient({ token: 'test-token' })
      expect(client.getToken()).toBe('test-token')
    })
  })

  describe('generate', () => {
    it('should generate a new token', async () => {
      const mockFetch = createMockFetch({
        success: true,
        token: 'word-word-word-word-word',
      })

      const client = new KeyValueClient({ fetch: mockFetch as any })
      const result = await client.generate()

      expect(result.token).toBe('word-word-word-word-word')
      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/generate',
        expect.objectContaining({
          method: 'POST',
        })
      )
    })

    it('should include turnstile token if provided', async () => {
      const mockFetch = createMockFetch({
        success: true,
        token: 'word-word-word-word-word',
      })

      const client = new KeyValueClient({ fetch: mockFetch as any })
      await client.generate('turnstile-token')

      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/generate',
        expect.objectContaining({
          body: JSON.stringify({ turnstileToken: 'turnstile-token' }),
        })
      )
    })
  })

  describe('store', () => {
    it('should store data with token', async () => {
      const mockFetch = createMockFetch({
        success: true,
        size: 100,
        tier: 'free',
        version: 1,
        updated_at: '2025-01-01T00:00:00Z',
        expires_at: null,
      })

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      const data = { test: 'value' }
      const result = await client.store(data)

      expect(result.success).toBe(true)
      expect(result.size).toBe(100)
      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/store',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ data }),
          headers: expect.objectContaining({
            'X-KV-Token': 'test-token',
          }),
        })
      )
    })

    it('should throw error if token not provided', async () => {
      const client = new KeyValueClient({ fetch: vi.fn() as any })

      await expect(client.store({ test: 'value' })).rejects.toThrow(
        'Token is required'
      )
    })

    it('should include TTL if provided', async () => {
      const mockFetch = createMockFetch({
        success: true,
        size: 100,
        tier: 'free',
        version: 1,
        updated_at: '2025-01-01T00:00:00Z',
        expires_at: '2025-01-01T01:00:00Z',
      })

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      await client.store({ test: 'value' }, { ttl: 3600 })

      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/store',
        expect.objectContaining({
          body: JSON.stringify({ data: { test: 'value' }, ttl: 3600 }),
        })
      )
    })
  })

  describe('retrieve', () => {
    it('should retrieve data with token', async () => {
      const mockFetch = createMockFetch({
        success: true,
        data: { test: 'value' },
        version: 1,
        updated_at: '2025-01-01T00:00:00Z',
        expires_at: null,
      })

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      const result = await client.retrieve()

      expect(result.data).toEqual({ test: 'value' })
      expect(result.version).toBe(1)
      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/retrieve',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'X-KV-Token': 'test-token',
          }),
        })
      )
    })

    it('should throw error if token not provided', async () => {
      const client = new KeyValueClient({ fetch: vi.fn() as any })

      await expect(client.retrieve()).rejects.toThrow('Token is required')
    })
  })

  describe('delete', () => {
    it('should delete data with token', async () => {
      const mockFetch = createMockFetch({
        success: true,
        message: 'Data deleted successfully',
      })

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      const result = await client.delete()

      expect(result.success).toBe(true)
      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/delete',
        expect.objectContaining({
          method: 'DELETE',
        })
      )
    })
  })

  describe('patch', () => {
    it('should patch data with version', async () => {
      const mockFetch = createMockFetch({
        success: true,
        version: 2,
        data: { count: 1 },
        updated_at: '2025-01-01T00:00:00Z',
        expires_at: null,
        size: 50,
        tier: 'free',
      })

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      const result = await client.patch({
        version: 1,
        patch: {
          set: { count: 1 },
        },
      })

      expect(result.version).toBe(2)
      expect(result.data).toEqual({ count: 1 })
      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/store',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({
            version: 1,
            patch: { set: { count: 1 } },
          }),
        })
      )
    })

    it('should handle conflict errors', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        json: async () => ({ error: 'Version conflict' }),
      })

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      await expect(
        client.patch({
          version: 1,
          patch: { set: { count: 1 } },
        })
      ).rejects.toThrow('Version conflict')
    })
  })

  describe('history', () => {
    it('should fetch history with default options', async () => {
      const mockFetch = createMockFetch({
        success: true,
        events: [],
        pagination: {
          limit: 50,
          before: null,
          since: null,
          has_more: false,
        },
      })

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      await client.history()

      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/history',
        expect.objectContaining({
          method: 'GET',
        })
      )
    })

    it('should include query parameters', async () => {
      const mockFetch = createMockFetch({
        success: true,
        events: [],
        pagination: { limit: 10, before: null, since: null, has_more: false },
      })

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      await client.history({
        limit: 10,
        before: 100,
        since: '2025-01-01T00:00:00Z',
        type: 'temperature',
      })

      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/history?limit=10&before=100&since=2025-01-01T00%3A00%3A00Z&type=temperature',
        expect.any(Object)
      )
    })
  })

  describe('batch', () => {
    it('should execute batch operations', async () => {
      const mockFetch = createMockFetch({
        success: true,
        results: [
          { success: true, token: 'token-1', action: 'store', version: 1 },
        ],
        summary: {
          total: 1,
          succeeded: 1,
          failed: 0,
          successRate: '100%',
        },
      })

      const client = new KeyValueClient({ fetch: mockFetch as any })

      const result = await client.batch([
        {
          action: 'store',
          token: 'token-1',
          data: { test: 'value' },
        },
      ])

      expect(result.summary.succeeded).toBe(1)
      expect(mockFetch).toHaveBeenCalledWith(
        'https://key-value.co/api/batch',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            operations: [
              {
                action: 'store',
                token: 'token-1',
                data: { test: 'value' },
              },
            ],
          }),
        })
      )
    })

    it('should throw error for empty operations', async () => {
      const client = new KeyValueClient({ fetch: vi.fn() as any })

      await expect(client.batch([])).rejects.toThrow(
        'At least one operation is required'
      )
    })

    it('should throw error for too many operations', async () => {
      const client = new KeyValueClient({ fetch: vi.fn() as any })
      const ops = Array(101).fill({ action: 'store', token: 'test', data: {} })

      await expect(client.batch(ops as any)).rejects.toThrow(
        'Maximum 100 operations'
      )
    })
  })

  describe('error handling', () => {
    it('should handle network errors', async () => {
      const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'))

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
      })

      await expect(client.retrieve()).rejects.toThrow('Network error')
    })

    it('should handle timeout', async () => {
      const mockFetch = vi.fn().mockImplementation(() =>
        new Promise(resolve => setTimeout(resolve, 100))
      )

      const client = new KeyValueClient({
        token: 'test-token',
        fetch: mockFetch as any,
        timeout: 50,
      })

      await expect(client.retrieve()).rejects.toThrow('timeout')
    })
  })
})
