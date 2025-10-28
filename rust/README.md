# Key-Value Rust Client

> Rust client for [Key-Value](https://key-value.co) - secure key-value store with memorable 5-word tokens.

## Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
keyvalue-client = "0.1"
```

## Quick Start

```rust
use keyvalue_client::{Client, Error};

#[tokio::main]
async fn main() -> Result<(), Error> {
    let client = Client::new("word-word-word-word-word");

    // Store data
    let data = serde_json::json!({"temperature": 23.5});
    let response = client.store(&data, None).await?;
    println!("Stored with version {}", response.version);

    // Retrieve data
    let result = client.retrieve().await?;
    println!("Data: {:?}", result.data);

    Ok(())
}
```

## Features

- ✅ Async/await with tokio
- ✅ Type-safe with serde
- ✅ Generate memorable tokens
- ✅ Store/Retrieve JSON data
- ✅ PATCH with optimistic concurrency
- ✅ Time-series history
- ✅ Batch operations
- ✅ Custom error types

## Examples

```bash
cargo run --example basic
cargo run --example batch
```

## Testing

```bash
cargo test
```

## License

MIT
