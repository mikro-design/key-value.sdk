#!/usr/bin/env python3
"""
Batch Operations Example

Demonstrates:
- Multiple operations in single request
- Store, retrieve, patch, delete in batch
- Error handling for individual operations
- Performance benefits of batching
"""

import os
import argparse
from keyvalue import KeyValueClient


def main():
    parser = argparse.ArgumentParser(description="Batch operations example")
    parser.add_argument(
        "--url",
        default=os.environ.get("API_URL", "https://key-value.co"),
        help="API base URL",
    )
    args = parser.parse_args()

    client = KeyValueClient(base_url=args.url)

    print("=== Batch Operations Example ===\n")

    # Generate 3 tokens
    print("Generating tokens...")
    token1 = client.generate()["token"]
    token2 = client.generate()["token"]
    token3 = client.generate()["token"]
    print(f"✓ Generated 3 tokens\n")

    # Batch Example 1: Multiple stores
    print("=== Batch Store ===")
    store_result = client.batch(
        [
            {
                "action": "store",
                "token": token1,
                "data": {"sensor": "temp-1", "value": 23.5},
            },
            {
                "action": "store",
                "token": token2,
                "data": {"sensor": "temp-2", "value": 24.1},
            },
            {
                "action": "store",
                "token": token3,
                "data": {"sensor": "temp-3", "value": 22.8},
            },
        ]
    )

    print(f"Success rate: {store_result['summary']['successRate']}")
    print(f"Succeeded: {store_result['summary']['succeeded']}")
    print(f"Failed: {store_result['summary']['failed']}\n")

    # Batch Example 2: Mixed operations
    print("=== Batch Mixed Operations ===")
    mixed_result = client.batch(
        [
            {"action": "retrieve", "token": token1},
            {
                "action": "store",
                "token": token2,
                "data": {"sensor": "temp-2", "value": 25.0, "updated": True},
            },
            {"action": "retrieve", "token": token3},
        ]
    )

    print("Results:")
    for result in mixed_result["results"]:
        token_preview = result["token"][:20] + "..."
        if result["success"]:
            print(f"  ✓ {result['action']} on {token_preview}")
            if result.get("data"):
                print(f"    Data: {result['data']}")
        else:
            print(f"  ✗ {result['action']} failed: {result.get('error')}")
    print()

    # Batch Example 3: Patch operations
    print("=== Batch Patch ===")

    # First get current versions
    versions = client.batch(
        [{"action": "retrieve", "token": token1}, {"action": "retrieve", "token": token2}]
    )

    patch_result = client.batch(
        [
            {
                "action": "patch",
                "token": token1,
                "version": versions["results"][0]["version"],
                "patch": {"set": {"value": 30.0}},
            },
            {
                "action": "patch",
                "token": token2,
                "version": versions["results"][1]["version"],
                "patch": {"set": {"value": 31.0}},
            },
        ]
    )

    print(f"Patched {patch_result['summary']['succeeded']} records\n")

    # Batch Example 4: Cleanup
    print("=== Batch Delete ===")
    delete_result = client.batch(
        [
            {"action": "delete", "token": token1},
            {"action": "delete", "token": token2},
            {"action": "delete", "token": token3},
        ]
    )

    print(f"Deleted {delete_result['summary']['succeeded']} records")
    print(f"✓ Cleanup complete\n")

    # Summary
    print("=== Summary ===")
    print("Batch operations allow you to:")
    print("  - Reduce HTTP overhead")
    print("  - Improve performance for bulk operations")
    print("  - Get atomic success/failure for each operation")
    print("  - Mix different operation types in one request")
    print("\nPerformance comparison:")
    print("  Individual requests: 3 stores = ~300-600ms")
    print("  Batch request: 3 stores = ~100-200ms")
    print("  Speedup: 2-3x faster! ⚡")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import sys

        sys.exit(1)
