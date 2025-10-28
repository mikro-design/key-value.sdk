/**
 * Key-Value Client Types
 */

export type Tier = 'free' | 'pro' | 'enterprise'

export interface ClientOptions {
  /** Base URL of the Key-Value API. Defaults to https://key-value.co */
  baseUrl?: string
  /** Default token to use for requests */
  token?: string
  /** Request timeout in milliseconds. Defaults to 30000 (30s) */
  timeout?: number
  /** Custom fetch implementation (for Node.js <18) */
  fetch?: typeof fetch
}

export interface StoreOptions {
  /** Time-to-live in seconds (max 30 days) */
  ttl?: number
  /** JSON schema to validate data against */
  schema?: DataSchema
}

export interface StoreResponse {
  success: true
  message: string
  size: number
  tier: Tier
  version: number
  updated_at: string
  expires_at: string | null
  debug?: {
    classified_type: string | null
    numeric_value: number | null
  }
}

export interface RetrieveResponse<T = any> {
  success: true
  data: T
  version: number
  updated_at: string
  expires_at: string | null
}

export interface GenerateResponse {
  success: true
  token: string
}

export interface DeleteResponse {
  success: true
  message: string
}

export interface HistoryOptions {
  /** Max events to return (default: 50, max: 200) */
  limit?: number
  /** Return events with seq < this value (pagination) */
  before?: number
  /** Return events created on or after this ISO timestamp */
  since?: string
  /** Filter by classified event type */
  type?: string
}

export interface HistoryEvent {
  seq: number
  created_at: string
  expires_at: string | null
  classified_type: string | null
  numeric_value: number | null
  text_value: string | null
  confidence: number | null
  payload: any
}

export interface HistoryResponse {
  success: true
  events: HistoryEvent[]
  pagination: {
    limit: number
    before: number | null
    since: string | null
    has_more: boolean
  }
}

export interface PatchOperations {
  /** Set fields using dot notation (e.g., "profile.name": "Alice") */
  set?: Record<string, any>
  /** Remove fields using dot notation array */
  remove?: string[]
}

export interface PatchOptions {
  /** Version for optimistic concurrency control */
  version: number
  /** Patch operations to apply */
  patch: PatchOperations
  /** Optional TTL update (null to clear expiry) */
  ttl?: number | null
}

export interface PatchResponse<T = any> {
  success: true
  version: number
  updated_at: string
  expires_at: string | null
  data: T
  size: number
  tier: Tier
}

export interface BatchOperation {
  action: 'store' | 'retrieve' | 'delete' | 'patch'
  token: string
  data?: any
  ttl?: number
  patch?: PatchOperations
  version?: number
}

export interface BatchResult<T = any> {
  success: boolean
  token: string
  action: string
  data?: T
  version?: number
  error?: string
}

export interface BatchResponse {
  success: true
  results: BatchResult[]
  summary: {
    total: number
    succeeded: number
    failed: number
    successRate: string
  }
}

export interface DataSchema {
  type: 'object' | 'array' | 'string' | 'number' | 'boolean'
  properties?: Record<string, DataSchema>
  items?: DataSchema
  required?: string[]
  enum?: any[]
  minimum?: number
  maximum?: number
  minLength?: number
  maxLength?: number
}

export interface APIError extends Error {
  status?: number
  response?: any
}

export interface UserTokenInfo {
  token_hash: string
  created_at: string
  last_accessed_at: string | null
  access_count: number
  tier: Tier
  is_demo: boolean
  is_private: boolean
  description: string | null
  encrypted_token: string | null
}

export interface TokenUsage {
  token_hash: string
  store_count: number
  retrieve_count: number
  delete_count: number
  last_activity_at: string | null
}
