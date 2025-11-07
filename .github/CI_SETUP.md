# CI/CD Setup Guide

This document explains the CI/CD pipelines and how to configure them.

## Overview

We have **5 automated workflows**:

1. **CI** - Main test suite (runs on every push)
2. **Integration Tests** - Tests against live API (daily + on-demand)
3. **Performance Benchmarks** - Tracks performance over time (daily)
4. **Coverage** - Code coverage reporting (on push to main/develop)
5. **Release** - Automated publishing to PyPI, npm, crates.io (on tags)

---

## Required GitHub Secrets

To enable all features, configure these secrets in your repository settings:

### Testing Secrets

| Secret Name | Purpose | How to Get |
|-------------|---------|------------|
| `KV_TEST_TOKEN` | Integration tests | Generate at https://key-value.co |

### Coverage Secrets

| Secret Name | Purpose | How to Get |
|-------------|---------|------------|
| `CODECOV_TOKEN` | Upload coverage reports | Sign up at https://codecov.io |

### Release Secrets

| Secret Name | Purpose | How to Get |
|-------------|---------|------------|
| `PYPI_TOKEN` | Publish Python to PyPI | https://pypi.org/manage/account/token/ |
| `TEST_PYPI_TOKEN` | Publish to Test PyPI (optional) | https://test.pypi.org/manage/account/token/ |
| `NPM_TOKEN` | Publish JavaScript to npm | https://www.npmjs.com/settings/~/tokens |
| `CARGO_TOKEN` | Publish Rust to crates.io | https://crates.io/settings/tokens |

**Note**: `GITHUB_TOKEN` is automatically provided by GitHub Actions.

---

## Workflow Details

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Every push to `main`, `develop`, or `claude/**` branches
- Every pull request to `main` or `develop`

**What it tests:**
- ✅ **Python**: 5 versions (3.8-3.12), all 13 examples
- ✅ **JavaScript**: 3 Node versions (18, 20, 22), all 4 examples
- ✅ **Go**: 3 versions (1.20-1.22), formatting, vet
- ✅ **Rust**: stable + beta, clippy, formatting
- ✅ **C**: Compilation with strict warnings, memory leak checks
- ✅ **Linting**: black, flake8, security scans
- ✅ **Docs**: Validates all documentation files

**Duration**: ~15-20 minutes

**Badge**:
```markdown
[![CI](https://github.com/mikro-design/key-value.sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/mikro-design/key-value.sdk/actions/workflows/ci.yml)
```

---

### 2. Integration Tests (`.github/workflows/integration.yml`)

**Triggers:**
- Daily at 2 AM UTC (scheduled)
- Manual dispatch (on-demand)
- Push to `main` branch

**What it tests:**
- **Python**: Generate token, store/retrieve, delete
- **JavaScript**: Generate token, store/retrieve, delete
- **Go**: Integration test suite (with `KV_TEST_TOKEN`)

**Required Secrets**: `KV_TEST_TOKEN` (optional for basic tests)

**On Failure**: Automatically creates a GitHub issue

---

### 3. Performance Benchmarks (`.github/workflows/benchmark.yml`)

**Triggers:**
- Daily at 3 AM UTC (scheduled)
- Push to `main` branch
- Pull requests

**What it measures:**
- API call latency (store, retrieve, batch)
- Memory usage
- Throughput

**Tracks trends over time** using GitHub Action Benchmark.

**Alert Threshold**: 150% regression (fails if performance drops significantly)

---

### 4. Coverage (`.github/workflows/coverage.yml`)

**Triggers:**
- Push to `main` or `develop`
- Pull requests

**What it tracks:**
- Python coverage (pytest-cov)
- JavaScript coverage (vitest)
- Go coverage (go test -cover)
- Rust coverage (cargo-llvm-cov)

**Uploads to**: [Codecov](https://codecov.io)

**Required Secrets**: `CODECOV_TOKEN`

**Badge**:
```markdown
[![codecov](https://codecov.io/gh/mikro-design/key-value.sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/mikro-design/key-value.sdk)
```

---

### 5. Release Automation (`.github/workflows/release.yml`)

**Triggers:**
- Push tags matching: `python-v*`, `javascript-v*`, `go-v*`, `rust-v*`, `c-v*`

**What it does:**

#### Python Release
1. Verifies version in `setup.py` matches tag
2. Builds wheel and source distribution
3. Publishes to PyPI (or Test PyPI for `-rc` versions)
4. Creates GitHub Release

**Required Secrets**: `PYPI_TOKEN`, `TEST_PYPI_TOKEN` (optional)

**Example**:
```bash
# Update version in python/setup.py to 0.2.0
git tag python-v0.2.0
git push origin python-v0.2.0
# Workflow publishes to PyPI automatically
```

#### JavaScript Release
1. Verifies version in `package.json` matches tag
2. Runs tests
3. Builds distribution
4. Publishes to npm (beta tag for `-beta`/`-rc`)
5. Creates GitHub Release

**Required Secrets**: `NPM_TOKEN`

**Example**:
```bash
# Update version in javascript/package.json to 0.3.0
npm version 0.3.0 --no-git-tag-version
git tag javascript-v0.3.0
git push origin javascript-v0.3.0
```

#### Go Release
1. Runs tests
2. Creates GitHub Release (Go modules use git tags)

**No secrets required** (Go modules published via git)

**Example**:
```bash
git tag go-v0.1.5
git push origin go-v0.1.5
```

#### Rust Release
1. Verifies version in `Cargo.toml` matches tag
2. Runs tests
3. Publishes to crates.io
4. Creates GitHub Release

**Required Secrets**: `CARGO_TOKEN`

**Example**:
```bash
# Update version in rust/Cargo.toml to 0.2.0
git tag rust-v0.2.0
git push origin rust-v0.2.0
```

#### C Release
1. Builds C SDK
2. Creates tarball
3. Creates GitHub Release with tarball as asset

**No secrets required** (distributed as source)

**Example**:
```bash
git tag c-v0.1.0
git push origin c-v0.1.0
```

---

## Dependabot (`.github/dependabot.yml`)

**What it does:**
- Checks for dependency updates weekly (Mondays at 9 AM)
- Creates PRs for security updates
- Monitors: Python, JavaScript, Go, Rust, GitHub Actions

**Configuration:**
- Max 5 PRs per language
- Auto-labeled with `dependencies` + language
- Ignores major version bumps (for stability)

---

## Setting Up Secrets

### 1. Navigate to Repository Settings
```
https://github.com/YOUR_ORG/key-value.sdk/settings/secrets/actions
```

### 2. Click "New repository secret"

### 3. Add each secret:

#### KV_TEST_TOKEN
```
Name: KV_TEST_TOKEN
Value: word-word-word-word-word
```
Generate at: https://key-value.co

#### CODECOV_TOKEN
```
Name: CODECOV_TOKEN
Value: <token from codecov.io>
```
1. Sign up at https://codecov.io
2. Add repository
3. Copy upload token

#### PYPI_TOKEN
```
Name: PYPI_TOKEN
Value: pypi-...
```
1. Go to https://pypi.org/manage/account/token/
2. Create token with "Entire account" scope (or specific project)
3. Copy token (starts with `pypi-`)

#### NPM_TOKEN
```
Name: NPM_TOKEN
Value: npm_...
```
1. Go to https://www.npmjs.com/settings/~/tokens
2. Create "Automation" token
3. Copy token

#### CARGO_TOKEN
```
Name: CARGO_TOKEN
Value: <token from crates.io>
```
1. Go to https://crates.io/settings/tokens
2. Create new token
3. Copy token

---

## Local Testing

### Run tests locally before pushing:

**Python**:
```bash
cd python
pytest tests/ -v --cov=keyvalue
python -m py_compile *.py
```

**JavaScript**:
```bash
cd javascript
npm test
npm run typecheck
npm run build
```

**Go**:
```bash
cd go
go test ./... -v
gofmt -l .
go vet ./...
```

**Rust**:
```bash
cd rust
cargo test
cargo fmt --check
cargo clippy
```

**C**:
```bash
cd c
make clean && make
```

---

## Troubleshooting

### CI Failing?

1. **Check the logs**: Click on the failing job in Actions tab
2. **Run locally**: Use the commands above to reproduce
3. **Secret missing**: Some features require secrets (see table above)

### Release Not Publishing?

1. **Check secrets**: Ensure tokens are configured
2. **Version mismatch**: Tag must match `setup.py`/`package.json`/`Cargo.toml`
3. **Tag format**: Must be `<lang>-v<version>` (e.g., `python-v0.2.0`)

### Integration Tests Failing?

1. **Check API status**: Visit https://key-value.co
2. **Token expired**: Generate new test token
3. **Rate limit**: Wait a few minutes and retry

---

## Maintenance

### Weekly Tasks
- Review Dependabot PRs
- Check integration test results
- Monitor performance benchmarks

### Monthly Tasks
- Review coverage reports
- Update dependencies manually if needed
- Check for security advisories

### Release Tasks
1. Update version in appropriate file:
   - Python: `python/setup.py` and `python/keyvalue/__init__.py`
   - JavaScript: `javascript/package.json`
   - Go: `go/version.go` (if exists)
   - Rust: `rust/Cargo.toml`
   - C: `c/version.h` (if exists)
2. Update CHANGELOG.md
3. Commit changes
4. Create and push tag
5. Monitor release workflow

---

## Questions?

- **CI Issues**: Open an issue with `ci` label
- **Release Problems**: Check [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Security**: See [SECURITY.md](../SECURITY.md)

---

**Last Updated**: November 7, 2025
