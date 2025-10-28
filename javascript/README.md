# Key-Value JavaScript/TypeScript Client

> Official TypeScript/JavaScript client for [Key-Value](https://key-value.co) - a secure key-value store with memorable 5-word tokens.

[![npm version](https://img.shields.io/npm/v/@keyvalue/client)](https://www.npmjs.com/package/@keyvalue/client)
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🔐 **Memorable Tokens** - 5-word tokens instead of UUIDs (`capable-germinate-disbelief-survival-quantum`)
- 📦 **Simple API** - Store, retrieve, patch, delete JSON data
- 📊 **Time-Series** - Full event history with versioning
- ⚡ **TypeScript First** - Full type safety out of the box
- 🚫 **No Signup Required** - Start using immediately (optional accounts for advanced features)
- 🔄 **Optimistic Concurrency** - PATCH with version-based conflict detection
- 📈 **Batch Operations** - Multiple operations in a single request
- 🌐 **Universal** - Works in Node.js, Deno, Bun, and browsers

## Installation

```bash
npm install @keyvalue/client
# or
yarn add @keyvalue/client
# or
pnpm add @keyvalue/client
```

## Quick Start

```typescript
import { KeyValueClient } from '@keyvalue/client'

const client = new KeyValueClient()

// Generate a memorable token
const { token } = await client.generate()
console.log(token) // "word-word-word-word-word"

// Store data
client.setToken(token)
await client.store({ temperature: 23.5, humidity: 45 })

// Retrieve data
const { data } = await client.retrieve()
console.log(data) // { temperature: 23.5, humidity: 45 }
```

## Usage

### Initialize Client

```typescript
import { KeyValueClient } from '@keyvalue/client'

// Default configuration (uses https://key-value.co)
const client = new KeyValueClient()

// Custom configuration
const client = new KeyValueClient({
  baseUrl: 'https://your-domain.com',
  token: 'your-default-token',
  timeout: 30000, // 30 seconds
})
```

### Generate Token

```typescript
// Generate a new 5-word token
const { token } = await client.generate()
console.log(token) // "capable-germinate-disbelief-survival-quantum"

// With Turnstile (bot protection)
const { token } = await client.generate('turnstile-response-token')
```

### Store Data

```typescript
// Store JSON data
await client.store({ user: 'alice', score: 100 }, { token: 'your-token' })

// With TTL (max 30 days)
await client.store(
  { temporary: 'data' },
  { token: 'your-token', ttl: 3600 } // 1 hour
)

// With schema validation
await client.store(
  { temperature: 23.5 },
  {
    token: 'your-token',
    schema: {
      type: 'object',
      properties: {
        temperature: { type: 'number', minimum: -40, maximum: 85 }
      },
      required: ['temperature']
    }
  }
)
```

### Retrieve Data

```typescript
// Retrieve data
const { data, version, updated_at, expires_at } = await client.retrieve('your-token')

// Using default token from client
client.setToken('your-token')
const { data } = await client.retrieve()
```

### PATCH (Atomic Updates)

```typescript
// Get current version
const { version } = await client.retrieve('your-token')

// Apply partial update
const result = await client.patch({
  token: 'your-token',
  version: version,
  patch: {
    set: {
      'profile.name': 'Alice',
      'stats.loginCount': 42
    },
    remove: ['deprecatedField']
  }
})

// With conflict retry logic
async function incrementCounter(client: KeyValueClient, token: string) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const { version, data } = await client.retrieve(token)
      return await client.patch({
        token,
        version,
        patch: {
          set: { count: (data.count || 0) + 1 }
        }
      })
    } catch (error) {
      if (error.status === 409 && attempt < 2) continue
      throw error
    }
  }
}
```

### History (Time-Series)

```typescript
// Get recent history
const history = await client.history({
  token: 'your-token',
  limit: 50 // default 50, max 200
})

// Filter by time
const recent = await client.history({
  token: 'your-token',
  since: '2025-01-01T00:00:00Z'
})

// Pagination
const older = await client.history({
  token: 'your-token',
  limit: 50,
  before: 100 // get events before seq 100
})

// Filter by event type
const filtered = await client.history({
  token: 'your-token',
  type: 'temperature'
})
```

### Batch Operations

```typescript
// Multiple operations in one request (max 100)
const result = await client.batch([
  {
    action: 'store',
    token: 'token-1',
    data: { sensor: 'temp-1', value: 23.5 }
  },
  {
    action: 'retrieve',
    token: 'token-2'
  },
  {
    action: 'delete',
    token: 'token-3'
  }
])

console.log(result.summary)
// {
//   total: 3,
//   succeeded: 3,
//   failed: 0,
//   successRate: "100%"
// }
```

### Delete Data

```typescript
await client.delete('your-token')
```

## Examples

See the [`examples/`](./examples) directory for complete examples:

- [`basic.ts`](./examples/basic.ts) - Store, retrieve, update
- [`patch.ts`](./examples/patch.ts) - Atomic updates with conflict handling
- [`history.ts`](./examples/history.ts) - Time-series queries and analytics
- [`batch.ts`](./examples/batch.ts) - Bulk operations

Run examples:

```bash
# Set your token
export KV_TOKEN="your-five-word-token"

# Run example
node --loader tsx examples/basic.ts
```

## API Reference

### `KeyValueClient`

#### Constructor

```typescript
new KeyValueClient(options?: ClientOptions)
```

**Options:**
- `baseUrl?: string` - API base URL (default: `https://key-value.co`)
- `token?: string` - Default token for requests
- `timeout?: number` - Request timeout in ms (default: 30000)
- `fetch?: typeof fetch` - Custom fetch implementation

#### Methods

- `generate(turnstileToken?: string): Promise<GenerateResponse>`
- `store<T>(data: T, options?: StoreOptions): Promise<StoreResponse>`
- `retrieve<T>(token?: string): Promise<RetrieveResponse<T>>`
- `delete(token?: string): Promise<DeleteResponse>`
- `history(options?: HistoryOptions): Promise<HistoryResponse>`
- `patch<T>(options: PatchOptions): Promise<PatchResponse<T>>`
- `batch(operations: BatchOperation[]): Promise<BatchResponse>`
- `setToken(token: string): void`
- `getToken(): string | undefined`

See [full type definitions](./src/types.ts) for details.

## Error Handling

```typescript
try {
  await client.store({ data: 'value' })
} catch (error) {
  console.error(error.message) // Error description
  console.error(error.status)  // HTTP status code
  console.error(error.response) // API response
}
```

Common errors:
- `400` - Invalid request (missing token, invalid data)
- `404` - Token not found
- `409` - Version conflict (PATCH)
- `413` - Payload too large (>100KB)
- `429` - Rate limit exceeded
- `500` - Server error

## TypeScript

Full TypeScript support with type inference:

```typescript
interface SensorData {
  temperature: number
  humidity: number
}

const { data } = await client.retrieve<SensorData>('your-token')
// data.temperature is typed as number
```

## Browser Usage

```typescript
// ES modules
import { KeyValueClient } from '@keyvalue/client'

// UMD (via CDN)
const { KeyValueClient } = window.KeyValue
```

## Related Projects

- [key-value.py](https://github.com/mikro-design/key-value.py) - Python client with examples
- [key-value.c](https://github.com/mikro-design/key-value.c) - C client for embedded systems
- [key-value.curl](https://github.com/mikro-design/key-value.curl) - curl examples

## License

MIT © [Your Name]

## Contributing

Contributions welcome! Please open an issue or PR.

## Links

- [Documentation](https://key-value.co/docs)
- [API Reference](https://key-value.co/api/docs)
- [GitHub](https://github.com/mikro-design/key-value.js)
- [npm](https://www.npmjs.com/package/@keyvalue/client)
