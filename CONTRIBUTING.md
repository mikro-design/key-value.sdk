# Contributing to Key-Value SDKs

Thank you for contributing! This monorepo contains SDKs for multiple languages.

## Repository Structure

```
key-value.sdk/
├── python/       # Python SDK
├── javascript/   # TypeScript/JavaScript SDK
├── c/            # C SDK
└── curl/         # curl examples
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

- [ ] Python implementation
- [ ] JavaScript implementation
- [ ] C implementation (if applicable)
- [ ] Examples for each SDK
- [ ] Tests for each SDK
- [ ] Documentation updates

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

### C
- Follow [Linux kernel style](https://www.kernel.org/doc/html/latest/process/coding-style.html)
- Use snake_case for functions
- Add comments for complex logic
- Check for memory leaks with valgrind

## Testing

All SDKs must have tests:

### Python
```bash
cd python
pytest tests/ -v --cov=keyvalue
```

### JavaScript
```bash
cd javascript
npm test
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

## Questions?

- Open an issue for bugs
- Start a discussion for feature requests
- Check existing issues before creating new ones

## Code of Conduct

Be respectful and constructive. This is a community project.
