#!/usr/bin/env python3
"""
Basic Key-Value Store Example

Demonstrates basic usage of the key-value web service with a pre-generated token:
- Store JSON data
- Retrieve the data
"""

import os
import argparse
import requests
import json
from typing import Dict, Any, Optional

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")


class KeyValueClient:
    """Simple client for the key-value store API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def store(self, token: str, data: Dict[Any, Any], ttl: Optional[int] = None) -> Dict:
        """
        Store JSON data with a token.

        Args:
            token: The 5-word token
            data: JSON-serializable data to store
            ttl: Optional time-to-live in seconds (max 30 days)

        Returns:
            Response data with success status and size
        """
        payload = {
            "data": data
        }
        if ttl:
            payload["ttl"] = ttl

        response = requests.post(
            f"{self.base_url}/api/store",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-KV-Token": token
            }
        )
        response.raise_for_status()
        return response.json()

    def retrieve(self, token: str) -> Dict:
        """
        Retrieve data for a token.

        Args:
            token: The 5-word token

        Returns:
            Response with data, version, updated_at, and expires_at
        """
        response = requests.get(
            f"{self.base_url}/api/retrieve",
            headers={"X-KV-Token": token}
        )
        response.raise_for_status()
        return response.json()


def main():
    """Demonstrate basic key-value store operations."""
    parser = argparse.ArgumentParser(description="Basic key-value store example")
    parser.add_argument(
        "--token",
        default=os.environ.get("KV_TOKEN"),
        help="Token to use (defaults to KV_TOKEN environment variable)",
    )
    args = parser.parse_args()

    if not args.token:
        print("Error: token is required. Provide --token or set KV_TOKEN.")
        return

    client = KeyValueClient(API_URL)

    token = args.token.strip()
    print("=== Using Provided Token ===")
    print(f"Token: {token}\n")

    # Step 2: Store some data
    print("=== Storing Data ===")
    my_data = {
        "user": "alice",
        "settings": {
            "theme": "dark",
            "notifications": True
        },
        "scores": [95, 87, 92]
    }

    result = client.store(token, my_data)
    print(f"Store result: {json.dumps(result, indent=2)}\n")

    # Step 3: Retrieve the data
    print("=== Retrieving Data ===")
    response = client.retrieve(token)
    retrieved = response['data']
    print(f"Retrieved data: {json.dumps(retrieved, indent=2)}")
    print(f"Version: {response.get('version')}")
    print(f"Updated at: {response.get('updated_at')}")
    print(f"Expires at: {response.get('expires_at', 'Never')}\n")

    # Verify data matches
    assert retrieved == my_data, "Data mismatch!"
    print("✓ Data successfully stored and retrieved!")

    # Step 4: Update the data
    print("\n=== Updating Data ===")
    my_data["settings"]["theme"] = "light"
    my_data["last_updated"] = "2025-10-13"

    result = client.store(token, my_data)
    print(f"Update result: {json.dumps(result, indent=2)}\n")

    # Retrieve updated data
    response = client.retrieve(token)
    updated = response['data']
    print(f"Updated data: {json.dumps(updated, indent=2)}")
    print(f"Version: {response.get('version')}")
    print(f"Updated at: {response.get('updated_at')}\n")
    assert updated == my_data, "Updated data mismatch!"
    print("✓ Data successfully updated!")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if e.response:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")
