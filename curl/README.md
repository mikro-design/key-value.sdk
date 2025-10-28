# key-value.curl

Executable curl walkthroughs for the Key-Value Store API. This directory can be pushed to a dedicated repository (e.g., `homing/key-value.curl`) to keep CLI-first examples isolated from the main app.

## Prerequisites

- `curl`
- `jq`

## Quick Start

```bash
make curl-example BASE_URL=https://key-value.co
```

You will be prompted for an existing token (or you can set `TOKEN` ahead of time). The demo will then:

1. Generate or reuse a token (`TOKEN` env var).
2. Store sample JSON with a timestamp.
3. Retrieve the stored payload.
4. Delete the payload (unless `SKIP_DELETE=1`).

Outputs are printed with helpful logging, and all responses are validated via `jq`.

## Environment Variables

- `BASE_URL` (default `https://key-value.co`) — target deployment.
- `TOKEN` — optional. Pre-set this if you prefer not to enter the token interactively.
- `SKIP_DELETE` — set to `1` to keep the stored payload after the run.

Example:

```bash
TOKEN=word-word-word-word-word make curl-example
```

## Continuous Integration

The GitHub Actions workflow at `.github/workflows/curl-example.yml` runs `make curl-example` on every push, pull request, or manual dispatch. To enable it:

1. Create a repository secret named `KV_TOKEN` that contains a valid token for the Key-Value API (GitHub → Settings → Secrets and variables → Actions).
2. Adjust the `BASE_URL` environment variable in the workflow if you need to target a different deployment.

## Files

- `run.sh` — orchestrates the curl workflow with error checking.
- `Makefile` — wraps the script with overridable environment variables.

## Using as a Standalone Repository

```bash
gh repo create homing/key-value.curl --public
git subtree split --prefix key-value.curl -b key-value-curl
git push origin key-value-curl:main
```

Alternatively, copy the directory to a fresh repository and push manually.
