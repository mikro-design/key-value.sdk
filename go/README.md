# Key-Value Go Client

> Go client for [Key-Value](https://key-value.co) - secure key-value store with memorable 5-word tokens.

## Installation

```bash
go get github.com/mikro-design/key-value.sdk/go
```

## Quick Start

```go
package main

import (
    "fmt"
    "log"

    kv "github.com/mikro-design/key-value.sdk/go"
)

func main() {
    client := kv.NewClient(kv.WithToken("word-word-word-word-word"))

    // Store data
    data := map[string]interface{}{"temperature": 23.5}
    resp, err := client.Store(data, "", nil)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Stored with version %d\n", resp.Version)

    // Retrieve data
    result, err := client.Retrieve("")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Data: %s\n", result.Data)
}
```

## Features

- ✅ Generate memorable 5-word tokens
- ✅ Store/Retrieve JSON data
- ✅ PATCH with optimistic concurrency
- ✅ Time-series history queries
- ✅ Batch operations
- ✅ Full type safety with structs
- ✅ Context support (coming soon)

## Documentation

See [examples/](./examples) for more usage examples.

## Testing

```bash
go test ./...
```

## License

MIT
