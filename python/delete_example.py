#!/usr/bin/env python3
"""
DELETE Example

Demonstrates how to delete stored data from the key-value store.

Features:
- Delete stored data permanently
- Verify deletion
- Safe deletion with confirmation
- Cleanup operations

Requirements:
    pip install requests

Usage:
    # Delete data for a token
    python delete_example.py --token YOUR-TOKEN delete

    # Delete with confirmation prompt
    python delete_example.py --token YOUR-TOKEN delete --confirm

    # Show current data before deleting
    python delete_example.py --token YOUR-TOKEN delete --show
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, Optional

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")


class KeyValueClient:
    """Simple client for key-value store operations."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token

    def store(self, data: Dict[Any, Any], ttl: Optional[int] = None) -> Dict:
        """Store data."""
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

    def retrieve(self) -> Optional[Dict[Any, Any]]:
        """Retrieve data. Returns None if not found."""
        try:
            response = requests.get(
                f"{self.base_url}/api/retrieve",
                headers={"X-KV-Token": self.token}
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def delete(self) -> Dict:
        """Delete stored data."""
        response = requests.delete(
            f"{self.base_url}/api/delete",
            headers={"X-KV-Token": self.token}
        )
        response.raise_for_status()
        return response.json()


def delete_data(args):
    """Delete data with optional confirmation."""
    client = KeyValueClient(API_URL, args.token)

    print("=== Delete Data ===\n")

    # Check if data exists
    print("Checking for existing data...")
    current = client.retrieve()

    if not current:
        print("✗ No data found for this token")
        print("  Nothing to delete\n")
        return

    # Show current data if requested
    if args.show:
        print("\nCurrent data:")
        print(f"  Version: {current.get('version')}")
        print(f"  Updated: {current.get('updated_at')}")
        print(f"  Expires: {current.get('expires_at', 'Never')}")
        print(f"  Data: {json.dumps(current.get('data'), indent=2)}\n")

    # Confirm deletion if requested
    if args.confirm:
        print("⚠ This will permanently delete all data for this token")
        response = input("Are you sure you want to delete? (yes/no): ").strip().lower()

        if response not in ['yes', 'y']:
            print("✓ Deletion cancelled\n")
            return

    # Perform deletion
    print("\nDeleting data...")
    result = client.delete()

    if result.get("success"):
        print("✓ Data deleted successfully\n")

        # Verify deletion
        print("Verifying deletion...")
        verify = client.retrieve()

        if verify is None:
            print("✓ Confirmed: No data found for token\n")
        else:
            print("⚠ Warning: Data still exists after deletion\n")
    else:
        print(f"✗ Deletion failed: {result.get('message', 'Unknown error')}\n")


def lifecycle_demo(args):
    """Demonstrate complete lifecycle: create, update, delete, verify."""
    client = KeyValueClient(API_URL, args.token)

    print("=== Complete Lifecycle Demo ===\n")

    # Step 1: Create
    print("1. Creating data...")
    data = {
        "demo": "lifecycle",
        "timestamp": "2025-10-23T10:00:00Z",
        "value": 42
    }
    result = client.store(data)
    print(f"   ✓ Created (version: {result.get('version')})\n")

    # Step 2: Verify creation
    print("2. Verifying data exists...")
    current = client.retrieve()
    print(f"   ✓ Data found (version: {current.get('version')})")
    print(f"   Value: {current['data']['value']}\n")

    # Step 3: Update
    print("3. Updating data...")
    data["value"] = 100
    data["updated"] = True
    result = client.store(data)
    print(f"   ✓ Updated (version: {result.get('version')})\n")

    # Step 4: Delete
    print("4. Deleting data...")
    result = client.delete()
    print(f"   ✓ Deleted\n")

    # Step 5: Verify deletion
    print("5. Verifying deletion...")
    verify = client.retrieve()

    if verify is None:
        print("   ✓ Confirmed: Data successfully deleted\n")
    else:
        print("   ✗ Error: Data still exists\n")

    # Step 6: Try to delete again (should fail)
    print("6. Attempting to delete again...")
    try:
        client.delete()
        print("   ✗ Unexpected: Second delete succeeded\n")
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print("   ✓ Expected: 404 Not Found (data already deleted)\n")
        else:
            print(f"   ✗ Unexpected error: {e}\n")

    print("✓ Lifecycle demo complete!")


def cleanup_expired(args):
    """Clean up expired or test data."""
    client = KeyValueClient(API_URL, args.token)

    print("=== Cleanup Utility ===\n")

    current = client.retrieve()

    if not current:
        print("✓ No data found - already clean\n")
        return

    data = current.get('data', {})
    expires_at = current.get('expires_at')

    print("Current data:")
    print(f"  Version: {current.get('version')}")
    print(f"  Updated: {current.get('updated_at')}")
    print(f"  Expires: {expires_at or 'Never'}")

    # Check if marked as test/demo data
    is_test = (
        data.get('demo') or
        data.get('test') or
        data.get('_test') or
        'test' in str(data.get('description', '')).lower()
    )

    if is_test:
        print("  Type: Test/Demo data\n")
    else:
        print("  Type: Regular data\n")

    # Decide whether to clean
    should_clean = False

    if args.force:
        should_clean = True
        print("Cleanup reason: --force flag specified")
    elif is_test:
        should_clean = True
        print("Cleanup reason: Test/demo data detected")
    elif expires_at:
        should_clean = True
        print("Cleanup reason: Data has expiration set")

    if should_clean:
        if not args.yes:
            response = input("\nProceed with cleanup? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("✓ Cleanup cancelled\n")
                return

        print("\nCleaning up...")
        result = client.delete()
        if result.get("success"):
            print("✓ Cleanup complete\n")
        else:
            print(f"✗ Cleanup failed: {result.get('message')}\n")
    else:
        print("No cleanup needed\n")


def main():
    global API_URL

    parser = argparse.ArgumentParser(
        description="Delete data from key-value store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple delete
  python delete_example.py --token YOUR-TOKEN delete

  # Delete with confirmation
  python delete_example.py --token YOUR-TOKEN delete --confirm

  # Show data before deleting
  python delete_example.py --token YOUR-TOKEN delete --show --confirm

  # Complete lifecycle demo
  python delete_example.py --token YOUR-TOKEN lifecycle

  # Cleanup test data
  python delete_example.py --token YOUR-TOKEN cleanup --yes
        """
    )

    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete stored data")
    delete_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Prompt for confirmation before deleting"
    )
    delete_parser.add_argument(
        "--show",
        action="store_true",
        help="Show current data before deleting"
    )

    # Lifecycle demo
    subparsers.add_parser("lifecycle", help="Full lifecycle demo (create, update, delete)")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up test/expired data")
    cleanup_parser.add_argument(
        "--force",
        action="store_true",
        help="Force cleanup regardless of data type"
    )
    cleanup_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return

    # Update API_URL if provided
    if args.url:
        API_URL = args.url

    if args.mode == "delete":
        delete_data(args)
    elif args.mode == "lifecycle":
        lifecycle_demo(args)
    elif args.mode == "cleanup":
        cleanup_expired(args)


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
