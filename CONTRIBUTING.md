# Contributing to Key-Value SDKs

Thank you for your interest in contributing to Key-Value! 🎉

We welcome contributions of all kinds: bug fixes, new features, documentation improvements, examples, and more. This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)
- [Recognition](#recognition)

## Code of Conduct

This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@key-value.co](mailto:conduct@key-value.co).

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/mikro-design/key-value.sdk/issues)
- Use the bug report template
- Include SDK version, OS, and reproduction steps
- Provide code samples if possible

### Suggesting Features

- Open a [Discussion](https://github.com/mikro-design/key-value.sdk/discussions) first
- Explain the use case and benefit
- Check the [Roadmap](./ROADMAP.md) to see if it's planned
- Consider implementing it yourself!

### Improving Documentation

- Fix typos, improve clarity, add examples
- Documentation PRs are always welcome
- No code changes needed - just edit the Markdown

### Contributing Code

- Bug fixes and small improvements: Submit a PR directly
- New features: Open a Discussion or Issue first
- Breaking changes: Require discussion and approval

## Repository Structure

```
key-value.sdk/
├── python/           # Python SDK + examples
├── javascript/       # TypeScript/JavaScript SDK
├── go/               # Go SDK
├── rust/             # Rust SDK
├── c/                # C SDK for embedded
└── curl/             # curl examples
```

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/key-value.sdk
   cd key-value.sdk
   ```
3. **Choose your language and work in that directory**

## Development Workflow

### Python SDK

```bash
cd python

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black keyvalue/
flake8 keyvalue/

# Add feature
vim keyvalue/client.py

# Add example
vim examples/my_feature_example.py
chmod +x examples/my_feature_example.py
```

### JavaScript SDK

```bash
cd javascript

# Install dependencies
npm install

# Run tests in watch mode
npm run test:watch

# Type check
npm run typecheck

# Build
npm run build

# Add feature
vim src/client.ts

# Add test
vim test/client.test.ts

# Add example
vim examples/my-feature.ts
```

### Go SDK

```bash
cd go

# Download dependencies
go mod download

# Run tests
go test ./... -v

# Format code
gofmt -w .
go vet ./...

# Add feature
vim client.go

# Add example
vim examples/my_feature.go

# Run example
go run examples/my_feature.go
```

### Rust SDK

```bash
cd rust

# Build
cargo build

# Run tests
cargo test

# Format code
cargo fmt

# Lint
cargo clippy

# Add feature
vim src/lib.rs

# Add example
vim examples/my_feature.rs

# Run example
cargo run --example my_feature
```

### C SDK

```bash
cd c

# Install dependencies (Ubuntu/Debian)
sudo apt-get install libcurl4-openssl-dev libjson-c-dev

# Build
make

# Run tests
make test

# Clean
make clean

# Add feature
vim src/keyvalue.c

# Add example
vim examples/my_feature.c
```

## Feature Parity

When adding a new feature, please implement it across all SDKs:

- [ ] Python implementation + tests + examples
- [ ] JavaScript/TypeScript implementation + tests + examples
- [ ] Go implementation + tests + examples
- [ ] Rust implementation + tests + examples
- [ ] C implementation (if applicable) + tests + examples
- [ ] Documentation updates (README for each SDK)
- [ ] Main README update

**Note**: For embedded-specific features (C SDK), cross-platform implementation may not be required.

## Code Style

### Python
- Use [Black](https://black.readthedocs.io/) formatter (line length: 100)
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Add type hints
- Docstrings for public functions

### JavaScript/TypeScript
- Use Prettier (configured in package.json)
- Follow TypeScript best practices
- Export all types
- JSDoc comments for public methods
- Prefer `async/await` over callbacks

### Go
- Run `gofmt` and `go vet` before committing
- Follow [Effective Go](https://golang.org/doc/effective_go)
- Use meaningful variable names
- Add comments for exported functions
- Handle errors explicitly

### Rust
- Run `cargo fmt` and `cargo clippy` before committing
- Follow [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- Use `Result<T, E>` for error handling
- Add doc comments (`///`) for public items
- Prefer idiomatic Rust patterns

### C
- Follow [Linux kernel style](https://www.kernel.org/doc/html/latest/process/coding-style.html)
- Use snake_case for functions
- Add comments for complex logic
- Check for memory leaks with valgrind
- Always free allocated memory

## Testing

All SDKs must have tests. Aim for >80% code coverage.

### Python
```bash
cd python
pytest tests/ -v --cov=keyvalue
```

### JavaScript
```bash
cd javascript
npm test              # Run all tests
npm run test:watch    # Watch mode for development
```

### Go
```bash
cd go
go test ./... -v      # All tests
go test -cover ./...  # With coverage
```

### Rust
```bash
cd rust
cargo test            # All tests
cargo test -- --nocapture  # With output
```

### C
```bash
cd c
make test
```

## Commit Messages

Use conventional commits:

```
feat(python): add batch API support
fix(js): handle timeout errors correctly
docs(c): update README with new examples
test(python): add tests for history pagination
chore(ci): upgrade Node.js to v20
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feat/add-batch-api
   ```

2. **Make your changes** in the relevant SDK directory

3. **Test your changes**
   ```bash
   # Run SDK-specific tests
   cd python && pytest
   cd javascript && npm test
   cd c && make test
   ```

4. **Commit with descriptive messages**
   ```bash
   git commit -m "feat(python): add batch API method"
   ```

5. **Push and create PR**
   ```bash
   git push origin feat/add-batch-api
   ```

6. **Fill out PR template** with:
   - What changed
   - Which SDKs affected
   - Breaking changes (if any)
   - Example usage

## Release Process

### Python (PyPI)
```bash
cd python
# Update version in setup.py and keyvalue/__init__.py
python setup.py sdist bdist_wheel
twine upload dist/*
git tag python-v0.1.0
```

### JavaScript (npm)
```bash
cd javascript
# Update version in package.json
npm run build
npm publish
git tag javascript-v0.1.0
```

### C
No formal release - users build from source.
```bash
git tag c-v0.1.0
```

## Recognition

We value and recognize all contributors!

### Ways We Recognize Contributors

- **CONTRIBUTORS.md**: All contributors listed with their contributions
- **GitHub**: Contributor badge on your profile
- **Release Notes**: Major contributions mentioned in changelogs
- **Social Media**: Shoutouts for significant features
- **Swag**: Free Key-Value swag for significant contributions (coming soon)

### Hall of Fame

Special recognition for contributors who:
- Add a new SDK for a language
- Write comprehensive documentation or tutorials
- Fix critical security issues
- Contribute 10+ PRs
- Help others in Discussions

## Community

### Get Help

- **GitHub Discussions**: [github.com/mikro-design/key-value.sdk/discussions](https://github.com/mikro-design/key-value.sdk/discussions)
- **Discord**: [discord.gg/keyvalue](https://discord.gg/keyvalue)
- **Email**: [hello@key-value.co](mailto:hello@key-value.co)

### Stay Updated

- **Watch this repo** for notifications
- **Star the repo** to show support
- **Follow [@keyvalue_co](https://twitter.com/keyvalue_co)** on Twitter
- **Subscribe** to our [newsletter](https://key-value.co/newsletter)

## Questions?

- Open an issue for bugs
- Start a discussion for feature requests
- Check existing issues before creating new ones
- Read the [Code of Conduct](./CODE_OF_CONDUCT.md)

---

**Thank you for contributing to Key-Value!** 🚀

Your contributions make this project better for everyone.
