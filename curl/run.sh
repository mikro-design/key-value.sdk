#!/usr/bin/env bash

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required to run this example. Install it and try again." >&2
  exit 1
fi

BASE_URL=${BASE_URL:-https://key-value.co}
TOKEN=${TOKEN:-}

log() {
  printf '==> %s\n' "$1"
}

ensure_token() {
  if [[ -n "$TOKEN" ]]; then
    log "Using provided token: $TOKEN"
    return
  fi

  read -rp "Enter an existing token (word-word-word-word-word): " TOKEN

  if [[ -z "$TOKEN" ]]; then
    echo "error: token is required. Retrieve one from the app first." >&2
    exit 1
  fi
}

store_payload() {
  log "Storing sample JSON payload"

  local payload
  payload=$(jq -n '{data: {message: "hello from curl", timestamp: (now | todateiso8601)}}')

  local response
  response=$(curl -sS -X POST "$BASE_URL/api/store" \
    -H "Content-Type: application/json" \
    -H "X-KV-Token: $TOKEN" \
    -d "$payload")

  local success
  success=$(jq -r '.success // false' <<<"$response")

  if [[ "$success" != "true" ]]; then
    echo "error: store request failed:" >&2
    echo "$response" >&2
    exit 1
  fi

  log "Store response: $response"
}

retrieve_payload() {
  log "Retrieving payload"

  local response
  response=$(curl -sS "$BASE_URL/api/retrieve" \
    -H "X-KV-Token: $TOKEN")

  local success
  success=$(jq -r '.success // false' <<<"$response")

  if [[ "$success" != "true" ]]; then
    echo "error: retrieve request failed:" >&2
    echo "$response" >&2
    exit 1
  fi

  log "Retrieve response:"
  jq '.' <<<"$response"
}

delete_payload() {
  if [[ "${SKIP_DELETE:-}" == "1" ]]; then
    log "Skipping delete (SKIP_DELETE=1)"
    return
  fi

  log "Deleting payload"

  local response
  response=$(curl -sS -X DELETE "$BASE_URL/api/delete" \
    -H "X-KV-Token: $TOKEN")

  local success
  success=$(jq -r '.success // empty' <<<"$response" || true)

  if [[ "$success" == "true" ]]; then
    log "Delete response: $response"
    return
  fi

  local error_message
  error_message=$(jq -r '.error // empty' <<<"$response" || true)

  if [[ -n "$error_message" ]]; then
    log "Delete returned error (continuing): $error_message"
    return
  fi

  echo "error: delete request produced an unexpected response:" >&2
  echo "$response" >&2
  exit 1
}

main() {
  log "Starting curl example (BASE_URL=$BASE_URL)"
  ensure_token
  store_payload
  retrieve_payload
  delete_payload
  log "All operations completed successfully"
}

main "$@"
