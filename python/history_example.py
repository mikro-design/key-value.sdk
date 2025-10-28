#!/usr/bin/env python3
"""
History API Example

Demonstrates the time-series event history API for tracking all changes
to a token over time.

Features:
- Query event history with filters
- Pagination support
- Filter by event type
- Time-based filtering
- Analyze event patterns
- Export history data

Requirements:
    pip install requests

Usage:
    # Generate some test data
    python history_example.py --token YOUR-TOKEN generate --count 20

    # View history
    python history_example.py --token YOUR-TOKEN view

    # View with filters
    python history_example.py --token YOUR-TOKEN view --limit 10 --type store

    # Analyze history
    python history_example.py --token YOUR-TOKEN analyze

    # Export to JSON
    python history_example.py --token YOUR-TOKEN export --output history.json
"""

import os
import sys
import json
import time
import argparse
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import Counter

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")


class KeyValueClient:
    """Client with history API support."""

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

    def patch(self, version: int, set_fields: Optional[Dict[str, Any]] = None,
              remove_fields: Optional[list] = None) -> Dict:
        """Apply partial update."""
        patch_ops = {}
        if set_fields:
            patch_ops["set"] = set_fields
        if remove_fields:
            patch_ops["remove"] = remove_fields

        response = requests.patch(
            f"{self.base_url}/api/store",
            json={
                "version": version,
                "patch": patch_ops
            },
            headers={
                "Content-Type": "application/json",
                "X-KV-Token": self.token
            }
        )
        response.raise_for_status()
        return response.json()

    def retrieve(self) -> Dict[Any, Any]:
        """Retrieve current data."""
        response = requests.get(
            f"{self.base_url}/api/retrieve",
            headers={"X-KV-Token": self.token}
        )
        response.raise_for_status()
        return response.json()

    def get_history(self, limit: int = 50, before: Optional[int] = None,
                   since: Optional[str] = None, event_type: Optional[str] = None) -> Dict:
        """
        Query event history.

        Args:
            limit: Max events to return (max: 200)
            before: Return events with seq < this value (for pagination)
            since: Return events created on or after this ISO timestamp
            event_type: Filter by classified event type

        Returns:
            Dict with events and pagination info
        """
        params = {"limit": limit}
        if before is not None:
            params["before"] = before
        if since:
            params["since"] = since
        if event_type:
            params["type"] = event_type

        response = requests.get(
            f"{self.base_url}/api/history",
            params=params,
            headers={"X-KV-Token": self.token}
        )
        response.raise_for_status()
        return response.json()

    def get_all_history(self, max_events: int = 1000) -> List[Dict]:
        """Fetch all history using pagination."""
        all_events = []
        before = None

        while len(all_events) < max_events:
            result = self.get_history(limit=200, before=before)
            events = result.get("events", [])

            if not events:
                break

            all_events.extend(events)

            if not result.get("pagination", {}).get("has_more"):
                break

            # Get seq of oldest event for next page
            before = events[-1]["seq"]

        return all_events[:max_events]


def generate_test_data(args):
    """Generate test data to create history."""
    client = KeyValueClient(API_URL, args.token)

    print(f"=== Generating {args.count} Test Events ===\n")

    # Initial store
    print("Creating initial data...")
    data = {
        "counter": 0,
        "status": "active",
        "metadata": {
            "created": datetime.utcnow().isoformat() + "Z",
            "source": "history_example"
        }
    }
    result = client.store(data)
    version = result["version"]
    print(f"✓ Initialized (version: {version})\n")

    # Generate random updates
    import random

    for i in range(1, args.count):
        action = random.choice(["increment", "status", "metadata"])

        if action == "increment":
            result = client.patch(
                version=version,
                set_fields={"counter": i}
            )
            print(f"[{i:3d}] Incremented counter to {i} (v{version} → v{result['version']})")

        elif action == "status":
            status = random.choice(["active", "idle", "busy", "maintenance"])
            result = client.patch(
                version=version,
                set_fields={"status": status}
            )
            print(f"[{i:3d}] Changed status to '{status}' (v{version} → v{result['version']})")

        elif action == "metadata":
            result = client.patch(
                version=version,
                set_fields={
                    "metadata.last_update": datetime.utcnow().isoformat() + "Z",
                    "metadata.update_count": i
                }
            )
            print(f"[{i:3d}] Updated metadata (v{version} → v{result['version']})")

        version = result["version"]
        time.sleep(args.interval)

    print(f"\n✓ Generated {args.count} events!")


def view_history(args):
    """View event history with formatting."""
    client = KeyValueClient(API_URL, args.token)

    print("=== Event History ===\n")

    # Build query parameters
    kwargs = {"limit": args.limit}
    if args.before:
        kwargs["before"] = args.before
    if args.since:
        kwargs["since"] = args.since
    if args.type:
        kwargs["event_type"] = args.type

    result = client.get_history(**kwargs)
    events = result.get("events", [])
    pagination = result.get("pagination", {})

    print(f"Showing {len(events)} events")
    if pagination.get("before"):
        print(f"  Before seq: {pagination['before']}")
    if pagination.get("since"):
        print(f"  Since: {pagination['since']}")
    print()

    if not events:
        print("No events found\n")
        return

    # Display events
    for event in events:
        seq = event.get("seq", "?")
        created = event.get("created_at", "")[:19]
        classified_type = event.get("classified_type") or "unclassified"
        numeric_value = event.get("numeric_value")
        text_value = event.get("text_value")

        payload = event.get("payload", {})
        event_type = payload.get("type", "unknown") if isinstance(payload, dict) else "unknown"

        # Format output
        print(f"[{seq:4d}] {created}")
        print(f"       Type: {event_type} (classified: {classified_type})")

        if numeric_value is not None:
            print(f"       Numeric: {numeric_value}")
        if text_value:
            print(f"       Text: {text_value}")

        # Show data preview
        if isinstance(payload, dict) and "data" in payload:
            data = payload["data"]
            if isinstance(data, dict):
                # Show a few key fields
                preview_keys = list(data.keys())[:3]
                preview = {k: data[k] for k in preview_keys}
                print(f"       Data: {json.dumps(preview)}")

                if len(data.keys()) > 3:
                    print(f"            ... and {len(data.keys()) - 3} more fields")

        print()

    # Pagination info
    if pagination.get("has_more"):
        oldest_seq = events[-1]["seq"]
        print(f"More events available. Use --before {oldest_seq} to fetch next page\n")
    else:
        print("No more events\n")


def analyze_history(args):
    """Analyze event history and show statistics."""
    client = KeyValueClient(API_URL, args.token)

    print("=== History Analysis ===\n")
    print("Fetching all events...")

    events = client.get_all_history(max_events=args.max_events)
    print(f"Loaded {len(events)} events\n")

    if not events:
        print("No events to analyze\n")
        return

    # Basic stats
    print("Basic Statistics:")
    print(f"  Total events: {len(events)}")
    print(f"  Oldest event: {events[-1].get('created_at', 'unknown')[:19]}")
    print(f"  Newest event: {events[0].get('created_at', 'unknown')[:19]}")

    # Event types
    types = [e.get("payload", {}).get("type", "unknown") for e in events if isinstance(e.get("payload"), dict)]
    type_counts = Counter(types)

    print(f"\nEvent Types:")
    for event_type, count in type_counts.most_common():
        print(f"  {event_type}: {count}")

    # Classified types
    classified = [e.get("classified_type") for e in events if e.get("classified_type")]
    if classified:
        classified_counts = Counter(classified)
        print(f"\nClassified Types:")
        for classified_type, count in classified_counts.most_common():
            print(f"  {classified_type}: {count}")

    # Numeric values
    numeric_values = [e.get("numeric_value") for e in events if e.get("numeric_value") is not None]
    if numeric_values:
        print(f"\nNumeric Values:")
        print(f"  Count: {len(numeric_values)}")
        print(f"  Min: {min(numeric_values)}")
        print(f"  Max: {max(numeric_values)}")
        print(f"  Avg: {sum(numeric_values) / len(numeric_values):.2f}")

    # Time-based analysis
    timestamps = [e.get("created_at") for e in events if e.get("created_at")]
    if len(timestamps) >= 2:
        first = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
        last = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
        duration = last - first

        print(f"\nTime Range:")
        print(f"  Duration: {duration}")
        if duration.total_seconds() > 0:
            rate = len(events) / duration.total_seconds()
            print(f"  Avg rate: {rate * 60:.2f} events/minute")

    print()


def export_history(args):
    """Export history to JSON file."""
    client = KeyValueClient(API_URL, args.token)

    print("=== Export History ===\n")
    print("Fetching all events...")

    events = client.get_all_history(max_events=args.max_events)
    print(f"Loaded {len(events)} events\n")

    if not events:
        print("No events to export\n")
        return

    # Prepare export data
    export_data = {
        "token": "***hidden***",
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "event_count": len(events),
        "events": events
    }

    # Write to file
    print(f"Writing to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"✓ Exported {len(events)} events to {args.output}\n")


def main():
    global API_URL

    parser = argparse.ArgumentParser(
        description="Query and analyze event history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate test data
  python history_example.py --token YOUR-TOKEN generate --count 20

  # View recent history
  python history_example.py --token YOUR-TOKEN view

  # View with filters
  python history_example.py --token YOUR-TOKEN view --limit 10 --type store

  # View events since a date
  python history_example.py --token YOUR-TOKEN view --since 2025-10-20T00:00:00Z

  # Analyze all history
  python history_example.py --token YOUR-TOKEN analyze

  # Export to file
  python history_example.py --token YOUR-TOKEN export --output history.json
        """
    )

    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate test events")
    gen_parser.add_argument("--count", type=int, default=20, help="Number of events to generate")
    gen_parser.add_argument("--interval", type=float, default=0.2, help="Interval between events (seconds)")

    # View command
    view_parser = subparsers.add_parser("view", help="View event history")
    view_parser.add_argument("--limit", type=int, default=50, help="Max events to show")
    view_parser.add_argument("--before", type=int, help="Show events before this seq")
    view_parser.add_argument("--since", help="Show events since this ISO timestamp")
    view_parser.add_argument("--type", help="Filter by event type")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze event history")
    analyze_parser.add_argument("--max-events", type=int, default=1000, help="Max events to analyze")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export history to JSON")
    export_parser.add_argument("--output", default="history.json", help="Output file")
    export_parser.add_argument("--max-events", type=int, default=1000, help="Max events to export")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return

    # Update API_URL if provided
    if args.url:
        API_URL = args.url

    if args.mode == "generate":
        generate_test_data(args)
    elif args.mode == "view":
        view_history(args)
    elif args.mode == "analyze":
        analyze_history(args)
    elif args.mode == "export":
        export_history(args)


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
