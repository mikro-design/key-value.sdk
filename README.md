# Key-Value SDKs

> Official client libraries for [Key-Value](https://key-value.co) - a secure key-value store with **memorable 5-word tokens**.

**Why Key-Value?**
- 🧠 **Memorable Tokens**: Share data with `capable-germinate-disbelief-survival-quantum` instead of `a8f7b2c9-4e3d-11ec-81d3-0242ac130003`
- 🛠️ **6 Production SDKs**: Python, JavaScript, Go, Rust, C, curl - all with feature parity
- 🌐 **IoT Ready**: Optimized C SDK for Raspberry Pi, ESP32, Arduino, and embedded systems
- 📊 **Time-Series History**: Built-in event log with classification and analytics
- ⚡ **Advanced Features**: Atomic PATCH operations, batch requests, schema validation, versioning

[![CI](https://github.com/mikro-design/key-value.sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/mikro-design/key-value.sdk/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/v/keyvalue-client?label=Python)](./python)
[![JavaScript](https://img.shields.io/npm/v/@keyvalue/client?label=JavaScript)](./javascript)
[![C](https://img.shields.io/badge/C-Ready-blue)](./c)
[![curl](https://img.shields.io/badge/curl-Examples-green)](./curl)

## 📚 Available SDKs

| Language | Directory | Installation | Status |
|----------|-----------|--------------|--------|
| **Python** | [`python/`](./python) | `pip install keyvalue-client` | ✅ Production Ready |
| **JavaScript/TypeScript** | [`javascript/`](./javascript) | `npm install @keyvalue/client` | ✅ Production Ready |
| **Go** | [`go/`](./go) | `go get github.com/mikro-design/key-value.sdk/go` | ✅ Production Ready |
| **Rust** | [`rust/`](./rust) | `cargo add keyvalue-client` | ✅ Production Ready |
| **C** | [`c/`](./c) | Build from source | ✅ Stable (Embedded/IoT) |
| **curl** | [`curl/`](./curl) | Copy scripts | ✅ Examples |

## 🚀 Quick Start

### Python
```python
from keyvalue import KeyValueClient

client = KeyValueClient(token="word-word-word-word-word")
client.store({"temperature": 23.5})
data = client.retrieve()
```

### JavaScript/TypeScript
```typescript
import { KeyValueClient } from '@keyvalue/client'

const client = new KeyValueClient({ token: 'word-word-word-word-word' })
await client.store({ temperature: 23.5 })
const { data } = await client.retrieve()
```

### Go
```go
import kv "github.com/mikro-design/key-value.sdk/go"

client := kv.NewClient(kv.WithToken("word-word-word-word-word"))
data := map[string]interface{}{"temperature": 23.5}
resp, _ := client.Store(data, "", nil)
result, _ := client.Retrieve("")
```

### Rust
```rust
use keyvalue_client::Client;

let client = Client::new("word-word-word-word-word");
let data = serde_json::json!({"temperature": 23.5});
let resp = client.store(&data, None).await?;
let result = client.retrieve().await?;
```

### C
```c
#include "keyvalue.h"

kv_client_t *client = kv_client_create("https://key-value.co");
kv_store(client, "word-word-word-word-word", "{\"temperature\":23.5}");
char *data = kv_retrieve(client, "word-word-word-word-word");
```

### curl
```bash
curl -X POST https://key-value.co/api/store \
  -H "X-KV-Token: word-word-word-word-word" \
  -H "Content-Type: application/json" \
  -d '{"data":{"temperature":23.5}}'
```

## ✨ Features

All SDKs support:

- ✅ **Memorable Tokens** - 5-word tokens (`capable-germinate-disbelief-survival-quantum`)
- ✅ **Store/Retrieve** - JSON data storage with versioning
- ✅ **PATCH** - Atomic partial updates with optimistic concurrency
- ✅ **History** - Time-series event log with filtering
- ✅ **Batch** - Multiple operations in single request
- ✅ **TTL** - Expiration support (max 30 days)
- ✅ **Error Handling** - Typed exceptions for rate limits, conflicts, etc.

### Language-Specific Features

| Feature | Python | JavaScript | Go | Rust | C | curl |
|---------|--------|------------|-------|------|---|------|
| Type Safety | ✅ Type hints | ✅ TypeScript | ✅ Structs | ✅ Strong | ✅ Structs | - |
| Examples | 11 scripts | 4 demos | 1 demo | 1 demo | 3 programs | Shell scripts |
| Package Manager | PyPI | npm | go get | cargo | Manual | - |
| Async | ✅ asyncio | ✅ Promise | ✅ Goroutines | ✅ tokio | - | - |
| Encryption | ✅ Example | - | - | - | - | - |
| IoT/Embedded | ✅ Sensors | ✅ Browser | ✅ Fast | ✅ Safe | ✅ Optimized | - |
| Clipboard Sync | ✅ | - | - | - | - | - |
| Webhooks | ✅ Receiver | - | - | - | - | - |

## 📖 Documentation

Each SDK has its own README with detailed usage:

- [Python Documentation](./python/README.md)
- [JavaScript Documentation](./javascript/README.md)
- [Go Documentation](./go/README.md)
- [Rust Documentation](./rust/README.md)
- [C Documentation](./c/README.md)
- [curl Documentation](./curl/README.md)

## 🔧 Development

### Repository Structure

```
key-value.sdk/
├── python/           # Python client + examples
│   ├── keyvalue/    # Installable package
│   ├── examples/    # 11 example scripts
│   ├── setup.py
│   └── README.md
├── javascript/      # TypeScript/JS client
│   ├── src/        # Source code
│   ├── examples/   # 4 example scripts
│   ├── test/       # Unit tests
│   └── README.md
├── go/             # Go client
│   ├── client.go   # Main implementation
│   ├── examples/   # Example programs
│   ├── go.mod
│   └── README.md
├── rust/           # Rust client
│   ├── src/        # Library source
│   ├── examples/   # Example programs
│   ├── Cargo.toml
│   └── README.md
├── c/              # C client for embedded systems
│   ├── src/        # Source files
│   ├── examples/   # 3 example programs
│   └── README.md
└── curl/           # Shell script examples
    ├── run.sh
    └── README.md
```

### Building from Source

#### Python
```bash
cd python
pip install -e .
python batch_example.py
```

#### JavaScript
```bash
cd javascript
npm install
npm run build
npm test
node examples/basic.ts
```

#### Go
```bash
cd go
go mod download
go run examples/basic.go
```

#### Rust
```bash
cd rust
cargo build
cargo run --example basic
```

#### C
```bash
cd c
make
./examples/basic_example
```

## 🧪 Testing

Each SDK includes tests:

```bash
# Python
cd python && pytest

# JavaScript
cd javascript && npm test

# Go
cd go && go test ./...

# Rust
cd rust && cargo test

# C
cd c && make test
```

## 📦 Publishing

### Python (PyPI)
```bash
cd python
python setup.py sdist bdist_wheel
twine upload dist/*
```

### JavaScript (npm)
```bash
cd javascript
npm run build
npm publish
```

### C
Distributed as source code - users build locally.

## 🤝 Contributing

Contributions welcome! Please:

1. Open an issue first to discuss changes
2. Follow existing code style for each language
3. Add tests for new features
4. Update documentation

### Feature Parity

When adding features, please implement across all SDKs:
- [ ] Feature added to Python
- [ ] Feature added to JavaScript
- [ ] Feature added to C (if applicable)
- [ ] Examples updated

## 💰 Pricing

**Free tier**: 100 requests/minute, 100KB payloads, 30-day TTL - perfect for development and small projects.

**Paid plans** available for production apps with higher limits, longer TTLs, and priority support.

See [PRICING.md](./PRICING.md) for detailed pricing and features.

## 🔒 Security

Security is our top priority. We use TLS 1.3, AES-256 encryption, and follow industry best practices.

- Encryption in transit and at rest
- Client-side encryption examples included
- SOC2 Type II certification in progress
- Regular security audits

See [SECURITY.md](./SECURITY.md) for our security policy and best practices.

## 📄 License

MIT © Key-Value Team

This software is open source and can be self-hosted. Paid plans support our managed cloud service with SLAs and support.

## 🔗 Links

- **Main Service**: [key-value.co](https://key-value.co)
- **API Docs**: [key-value.co/api/docs](https://key-value.co/api/docs)
- **Main Repo**: [github.com/mikro-design/key-value](https://github.com/mikro-design/key-value)
- **Issues**: [github.com/mikro-design/key-value.sdk/issues](https://github.com/mikro-design/key-value.sdk/issues)

## 🌟 Related

- [key-value](https://github.com/mikro-design/key-value) - Main Next.js application
- [key-value.curl](https://github.com/mikro-design/key-value.curl) - Standalone curl package (deprecated, use `curl/` here)

---

**Note**: This is a monorepo containing all official SDKs. Previously maintained as separate repos (key-value.py, key-value.js, key-value.c) - now consolidated for easier maintenance.
