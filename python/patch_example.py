#!/usr/bin/env python3
"""
PATCH Example - Optimistic Concurrency Control

Demonstrates atomic partial updates using the PATCH endpoint with version-based
conflict detection. This is crucial for scenarios with multiple writers.

Features:
- Atomic partial updates with dot-notation paths
- Version-based optimistic locking
- Conflict detection and retry logic
- Set nested fields
- Remove fields
- Update TTL independently

Requirements:
    pip install requests

Usage:
    # Basic patch operations
    python patch_example.py --token YOUR-TOKEN demo

    # Concurrent counter simulation
    python patch_example.py --token YOUR-TOKEN counter --writers 5

    # Nested object updates
    python patch_example.py --token YOUR-TOKEN nested
"""

import os
import sys
import time
import json
import argparse
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import random

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")


class KeyValueClient:
    """Client with PATCH support for optimistic concurrency."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token

    def store(self, data: Dict[Any, Any], ttl: Optional[int] = None) -> Dict:
        """Store data with POST."""
        payload = {"data": data}
        if ttl is not None:
            payload["ttl"] = ttl

        response = requests.post(
            f"{self.base_url}/api/store",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-KV-Token": self.token
            }
        )
        response.raise_for_status()
        return response.json()

    def patch(self, version: int, set_fields: Optional[Dict[str, Any]] = None,
              remove_fields: Optional[list] = None, ttl: Optional[int] = None) -> Dict:
        """
        Apply partial update with optimistic locking.

        Args:
            version: Current version (from previous GET/POST/PATCH)
            set_fields: Dict of dot-notation paths to set (e.g., {"stats.count": 42})
            remove_fields: List of dot-notation paths to remove
            ttl: Optional new TTL in seconds (use None to leave unchanged)

        Returns:
            Response with new version and updated data

        Raises:
            requests.HTTPError: 409 if version conflict detected
        """
        patch_ops = {}
        if set_fields:
            patch_ops["set"] = set_fields
        if remove_fields:
            patch_ops["remove"] = remove_fields

        payload = {
            "version": version,
            "patch": patch_ops
        }

        if ttl is not None:
            payload["ttl"] = ttl

        response = requests.patch(
            f"{self.base_url}/api/store",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-KV-Token": self.token
            }
        )
        response.raise_for_status()
        return response.json()

    def retrieve(self) -> Dict[Any, Any]:
        """Retrieve current data with version."""
        response = requests.get(
            f"{self.base_url}/api/retrieve",
            headers={"X-KV-Token": self.token}
        )
        response.raise_for_status()
        return response.json()

    def delete(self) -> Dict:
        """Delete stored data."""
        response = requests.delete(
            f"{self.base_url}/api/delete",
            headers={"X-KV-Token": self.token}
        )
        response.raise_for_status()
        return response.json()


def demo_basic_patch(args):
    """Demonstrate basic PATCH operations."""
    print("=== Basic PATCH Demo ===\n")

    client = KeyValueClient(API_URL, args.token)

    # Step 1: Initialize data
    print("1. Initializing data...")
    initial_data = {
        "user": "alice",
        "profile": {
            "name": "Alice Smith",
            "email": "alice@example.com"
        },
        "settings": {
            "theme": "dark",
            "notifications": True
        },
        "stats": {
            "loginCount": 10,
            "lastLogin": "2025-10-20"
        }
    }

    result = client.store(initial_data)
    version = result["version"]
    print(f"   Stored (version: {version})")
    print(f"   Data: {json.dumps(initial_data, indent=2)}\n")

    # Step 2: Update nested field
    print("2. Updating nested field (profile.name)...")
    result = client.patch(
        version=version,
        set_fields={"profile.name": "Alice Johnson"}
    )
    version = result["version"]
    print(f"   Success (version: {version})")
    print(f"   Updated name: {result['data']['profile']['name']}\n")

    # Step 3: Update multiple fields
    print("3. Updating multiple fields...")
    result = client.patch(
        version=version,
        set_fields={
            "stats.loginCount": 11,
            "stats.lastLogin": datetime.utcnow().strftime("%Y-%m-%d"),
            "settings.theme": "light"
        }
    )
    version = result["version"]
    print(f"   Success (version: {version})")
    print(f"   Stats: {result['data']['stats']}")
    print(f"   Theme: {result['data']['settings']['theme']}\n")

    # Step 4: Remove fields
    print("4. Removing fields...")
    result = client.patch(
        version=version,
        remove_fields=["settings.notifications"]
    )
    version = result["version"]
    print(f"   Success (version: {version})")
    print(f"   Settings: {result['data']['settings']}\n")

    # Step 5: Add new fields
    print("5. Adding new nested structure...")
    result = client.patch(
        version=version,
        set_fields={
            "preferences.language": "en",
            "preferences.timezone": "UTC"
        }
    )
    version = result["version"]
    print(f"   Success (version: {version})")
    print(f"   Preferences: {result['data']['preferences']}\n")

    # Step 6: Final state
    print("6. Final state:")
    current = client.retrieve()
    print(f"   Version: {current['version']}")
    print(f"   Data: {json.dumps(current['data'], indent=2)}\n")

    print("✓ Basic PATCH demo complete!")


def demo_concurrent_counter(args):
    """Simulate concurrent writers with conflict resolution."""
    print("=== Concurrent Counter Demo ===\n")
    print(f"Simulating {args.writers} concurrent writers")
    print("Each writer increments the counter independently\n")

    client = KeyValueClient(API_URL, args.token)

    # Initialize counter
    print("Initializing counter...")
    result = client.store({"counter": 0, "writers": {}})
    print(f"Counter initialized (version: {result['version']})\n")

    # Simulate concurrent writers
    stats = {
        "total_attempts": 0,
        "successful_updates": 0,
        "conflicts": 0,
        "retries": 0
    }

    for writer_id in range(1, args.writers + 1):
        print(f"Writer {writer_id} attempting to increment...")

        max_retries = 10
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            stats["total_attempts"] += 1

            try:
                # Get current version and counter value
                current = client.retrieve()
                version = current["version"]
                counter = current["data"]["counter"]

                # Simulate some processing time (increases chance of conflict)
                time.sleep(random.uniform(0.1, 0.3))

                # Attempt to increment
                result = client.patch(
                    version=version,
                    set_fields={
                        "counter": counter + 1,
                        f"writers.writer_{writer_id}": {
                            "increments": 1,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    }
                )

                new_version = result["version"]
                new_counter = result["data"]["counter"]

                print(f"   ✓ Success! Counter: {counter} → {new_counter} "
                      f"(v{version} → v{new_version})")

                if retry_count > 0:
                    print(f"     (succeeded after {retry_count} retries)")

                stats["successful_updates"] += 1
                stats["retries"] += retry_count
                success = True

            except requests.HTTPError as e:
                if e.response.status_code == 409:
                    # Conflict detected - another writer updated first
                    retry_count += 1
                    stats["conflicts"] += 1
                    print(f"   ⚠ Conflict detected, retrying... (attempt {retry_count})")
                    time.sleep(random.uniform(0.05, 0.15))
                else:
                    raise

        if not success:
            print(f"   ✗ Failed after {max_retries} retries")

    # Final results
    print("\n=== Results ===")
    final = client.retrieve()
    print(f"Final counter value: {final['data']['counter']}")
    print(f"Final version: {final['version']}")
    print(f"\nStatistics:")
    print(f"  Total attempts: {stats['total_attempts']}")
    print(f"  Successful updates: {stats['successful_updates']}")
    print(f"  Conflicts encountered: {stats['conflicts']}")
    print(f"  Average retries per writer: {stats['retries'] / args.writers:.1f}")
    print(f"\n✓ All writers completed successfully!")


def demo_nested_updates(args):
    """Demonstrate complex nested object updates."""
    print("=== Nested Object Updates Demo ===\n")

    client = KeyValueClient(API_URL, args.token)

    # Initialize complex nested structure
    print("1. Initializing nested structure...")
    data = {
        "company": "Acme Corp",
        "departments": {
            "engineering": {
                "headcount": 50,
                "budget": 5000000,
                "projects": ["api", "dashboard", "mobile"]
            },
            "sales": {
                "headcount": 30,
                "budget": 2000000,
                "quota": 10000000
            }
        },
        "metrics": {
            "revenue": 8000000,
            "growth": 0.25
        }
    }

    result = client.store(data)
    version = result["version"]
    print(f"   Stored (version: {version})\n")

    # Update multiple nested fields
    print("2. Updating engineering department...")
    result = client.patch(
        version=version,
        set_fields={
            "departments.engineering.headcount": 55,
            "departments.engineering.budget": 5500000,
            "departments.engineering.lead": "Alice Johnson"
        }
    )
    version = result["version"]
    print(f"   ✓ Updated (version: {version})")
    print(f"   Engineering: {json.dumps(result['data']['departments']['engineering'], indent=4)}\n")

    # Add new department
    print("3. Adding marketing department...")
    result = client.patch(
        version=version,
        set_fields={
            "departments.marketing.headcount": 20,
            "departments.marketing.budget": 3000000,
            "departments.marketing.channels": ["social", "email", "ads"]
        }
    )
    version = result["version"]
    print(f"   ✓ Added (version: {version})")
    print(f"   Marketing: {json.dumps(result['data']['departments']['marketing'], indent=4)}\n")

    # Update metrics
    print("4. Updating company metrics...")
    result = client.patch(
        version=version,
        set_fields={
            "metrics.revenue": 9000000,
            "metrics.growth": 0.30,
            "metrics.employees": 105
        }
    )
    version = result["version"]
    print(f"   ✓ Updated (version: {version})")
    print(f"   Metrics: {json.dumps(result['data']['metrics'], indent=4)}\n")

    # Remove obsolete field
    print("5. Removing sales quota field...")
    result = client.patch(
        version=version,
        remove_fields=["departments.sales.quota"]
    )
    version = result["version"]
    print(f"   ✓ Removed (version: {version})\n")

    # Final state
    print("6. Final structure:")
    final = client.retrieve()
    print(f"   Version: {final['version']}")
    print(f"   Departments: {list(final['data']['departments'].keys())}")
    print(f"   Total employees: {sum(d.get('headcount', 0) for d in final['data']['departments'].values())}")
    print(f"\n✓ Nested updates demo complete!")


def main():
    global API_URL

    parser = argparse.ArgumentParser(
        description="PATCH endpoint examples with optimistic concurrency",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic PATCH operations
  python patch_example.py --token YOUR-TOKEN demo

  # Concurrent counter with 5 writers
  python patch_example.py --token YOUR-TOKEN counter --writers 5

  # Nested object updates
  python patch_example.py --token YOUR-TOKEN nested
        """
    )

    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="mode", help="Demo mode")

    # Basic demo
    subparsers.add_parser("demo", help="Basic PATCH operations")

    # Concurrent counter
    counter_parser = subparsers.add_parser("counter", help="Concurrent counter simulation")
    counter_parser.add_argument(
        "--writers",
        type=int,
        default=5,
        help="Number of concurrent writers (default: 5)"
    )

    # Nested updates
    subparsers.add_parser("nested", help="Complex nested object updates")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return

    # Update API_URL if provided
    if args.url:
        API_URL = args.url

    if args.mode == "demo":
        demo_basic_patch(args)
    elif args.mode == "counter":
        demo_concurrent_counter(args)
    elif args.mode == "nested":
        demo_nested_updates(args)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP Error: {e}", file=sys.stderr)
        if e.response:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
