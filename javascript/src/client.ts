import type {
  ClientOptions,
  StoreOptions,
  StoreResponse,
  RetrieveResponse,
  GenerateResponse,
  DeleteResponse,
  HistoryOptions,
  HistoryResponse,
  PatchOptions,
  PatchResponse,
  BatchOperation,
  BatchResponse,
  APIError,
} from './types'

const DEFAULT_BASE_URL = 'https://key-value.co'
const DEFAULT_TIMEOUT = 30000

export class KeyValueClient {
  private baseUrl: string
  private token?: string
  private timeout: number
  private fetchImpl: typeof fetch

  constructor(options: ClientOptions = {}) {
    this.baseUrl = options.baseUrl?.replace(/\/$/, '') || DEFAULT_BASE_URL
    this.token = options.token
    this.timeout = options.timeout || DEFAULT_TIMEOUT
    this.fetchImpl = options.fetch || globalThis.fetch

    if (!this.fetchImpl) {
      throw new Error(
        'Fetch is not available. Please provide a fetch implementation or use Node.js >=18'
      )
    }
  }

  /**
   * Generate a new 5-word memorable token
   */
  async generate(turnstileToken?: string): Promise<GenerateResponse> {
    const body = turnstileToken ? { turnstileToken } : undefined
    return this.request<GenerateResponse>('/api/generate', {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
      skipTokenHeader: true,
    })
  }

  /**
   * Store JSON data with a token
   */
  async store<T = any>(
    data: T,
    options: StoreOptions & { token?: string } = {}
  ): Promise<StoreResponse> {
    const token = options.token || this.token
    if (!token) {
      throw this.createError('Token is required for store operation')
    }

    const payload: any = { data }
    if (options.ttl !== undefined) payload.ttl = options.ttl
    if (options.schema !== undefined) payload.schema = options.schema

    return this.request<StoreResponse>('/api/store', {
      method: 'POST',
      body: JSON.stringify(payload),
      token,
    })
  }

  /**
   * Retrieve data for a token
   */
  async retrieve<T = any>(token?: string): Promise<RetrieveResponse<T>> {
    const authToken = token || this.token
    if (!authToken) {
      throw this.createError('Token is required for retrieve operation')
    }

    return this.request<RetrieveResponse<T>>('/api/retrieve', {
      method: 'GET',
      token: authToken,
    })
  }

  /**
   * Delete data for a token
   */
  async delete(token?: string): Promise<DeleteResponse> {
    const authToken = token || this.token
    if (!authToken) {
      throw this.createError('Token is required for delete operation')
    }

    return this.request<DeleteResponse>('/api/delete', {
      method: 'DELETE',
      token: authToken,
    })
  }

  /**
   * Query event history for a token
   */
  async history(options: HistoryOptions & { token?: string } = {}): Promise<HistoryResponse> {
    const token = options.token || this.token
    if (!token) {
      throw this.createError('Token is required for history operation')
    }

    const params = new URLSearchParams()
    if (options.limit !== undefined) params.set('limit', String(options.limit))
    if (options.before !== undefined) params.set('before', String(options.before))
    if (options.since !== undefined) params.set('since', options.since)
    if (options.type !== undefined) params.set('type', options.type)

    const url = `/api/history${params.toString() ? `?${params.toString()}` : ''}`

    return this.request<HistoryResponse>(url, {
      method: 'GET',
      token,
    })
  }

  /**
   * Apply atomic partial updates with optimistic concurrency
   */
  async patch<T = any>(
    options: PatchOptions & { token?: string }
  ): Promise<PatchResponse<T>> {
    const token = options.token || this.token
    if (!token) {
      throw this.createError('Token is required for patch operation')
    }

    const { version, patch, ttl } = options
    const payload: any = { version, patch }
    if (ttl !== undefined) payload.ttl = ttl

    return this.request<PatchResponse<T>>('/api/store', {
      method: 'PATCH',
      body: JSON.stringify(payload),
      token,
    })
  }

  /**
   * Execute multiple operations in a single request
   */
  async batch(operations: BatchOperation[]): Promise<BatchResponse> {
    if (operations.length === 0) {
      throw this.createError('At least one operation is required')
    }
    if (operations.length > 100) {
      throw this.createError('Maximum 100 operations per batch request')
    }

    return this.request<BatchResponse>('/api/batch', {
      method: 'POST',
      body: JSON.stringify({ operations }),
      skipTokenHeader: true,
    })
  }

  /**
   * Set the default token for subsequent requests
   */
  setToken(token: string): void {
    this.token = token
  }

  /**
   * Get the current default token
   */
  getToken(): string | undefined {
    return this.token
  }

  /**
   * Internal request handler
   */
  private async request<T>(
    path: string,
    options: {
      method: string
      body?: string
      token?: string
      skipTokenHeader?: boolean
    }
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (options.token && !options.skipTokenHeader) {
      headers['X-KV-Token'] = options.token
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const response = await this.fetchImpl(url, {
        method: options.method,
        headers,
        body: options.body,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      const data = await response.json()

      if (!response.ok) {
        throw this.createError(data.error || `HTTP ${response.status}`, response.status, data)
      }

      return data as T
    } catch (error: any) {
      clearTimeout(timeoutId)

      if (error.name === 'AbortError') {
        throw this.createError(`Request timeout after ${this.timeout}ms`)
      }

      throw error
    }
  }

  /**
   * Create a typed API error
   */
  private createError(message: string, status?: number, response?: any): APIError {
    const error = new Error(message) as APIError
    error.name = 'KeyValueError'
    error.status = status
    error.response = response
    return error
  }
}
