#!/usr/bin/env python3
"""
IP Tracker Service

A service that periodically checks your external IP address and stores it
in the key-value store. Useful for tracking your home network's IP when
you're away, especially with dynamic IP addresses.

Features:
- Automatically detects external IP
- Stores IP with timestamp and metadata
- Periodic updates (configurable interval)
- Email notification on IP change (optional)
- Can run as a daemon/service

Requirements:
    pip install requests

Usage:
    # One-time update
    python ip_tracker.py --token YOUR-TOKEN update

    # Monitor mode (updates every 5 minutes)
    python ip_tracker.py --token YOUR-TOKEN monitor --interval 300

    # Get current stored IP
    python ip_tracker.py --token YOUR-TOKEN get
"""

import os
import requests
import json
import time
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")
IP_CHECK_SERVICES = [
    "https://api.ipify.org?format=json",
    "https://ifconfig.me/ip",
    "https://icanhazip.com",
]


class IPTracker:
    """Track external IP address using key-value store."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token

    def get_external_ip(self) -> str:
        """Get external IP from multiple services (with fallback)."""
        for service in IP_CHECK_SERVICES:
            try:
                response = requests.get(service, timeout=5)
                response.raise_for_status()

                # Parse response based on content type
                if "json" in response.headers.get("content-type", ""):
                    return response.json()["ip"]
                else:
                    return response.text.strip()
            except Exception as e:
                print(f"Failed to get IP from {service}: {e}", file=sys.stderr)
                continue

        raise Exception("Failed to get external IP from all services")

    def store_ip(self, ip_data: Dict[Any, Any]) -> Dict:
        """Store IP data in key-value store."""
        response = requests.post(
            f"{self.base_url}/api/store",
            json={"data": ip_data},
            headers={
                "Content-Type": "application/json",
                "X-KV-Token": self.token
            }
        )
        response.raise_for_status()
        return response.json()

    def get_stored_ip(self) -> Optional[Dict[Any, Any]]:
        """Retrieve stored IP data."""
        try:
            response = requests.get(
                f"{self.base_url}/api/retrieve",
                headers={"X-KV-Token": self.token}
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 404:
                return None
            raise

    def update_ip(self) -> Dict[str, Any]:
        """Check current IP and update if changed."""
        # Get current external IP
        current_ip = self.get_external_ip()

        # Get stored data
        stored = self.get_stored_ip()
        previous_ip = stored["ip"] if stored else None

        # Check if IP changed
        ip_changed = current_ip != previous_ip

        # Prepare data to store
        ip_data = {
            "ip": current_ip,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "changed": ip_changed,
            "previous_ip": previous_ip,
        }

        # Add history
        if stored and "history" in stored:
            history = stored["history"][-9:]  # Keep last 10 entries
        else:
            history = []

        if ip_changed and previous_ip:
            history.append({
                "ip": previous_ip,
                "timestamp": stored.get("last_updated") if stored else None,
            })

        ip_data["history"] = history

        # Store
        result = self.store_ip(ip_data)

        return {
            "current_ip": current_ip,
            "previous_ip": previous_ip,
            "changed": ip_changed,
            "stored": result,
        }

    def monitor(self, interval: int = 300, max_runs: Optional[int] = None):
        """
        Continuously monitor IP and update on changes.

        Args:
            interval: Check interval in seconds (default 5 minutes)
            max_runs: Maximum number of checks (None = infinite)
        """
        runs = 0
        print(f"Starting IP monitor (checking every {interval}s)")
        print(f"Press Ctrl+C to stop\n")

        try:
            while max_runs is None or runs < max_runs:
                runs += 1

                try:
                    result = self.update_ip()

                    if result["changed"]:
                        print(f"[{datetime.now()}] IP CHANGED!")
                        print(f"  Old: {result['previous_ip']}")
                        print(f"  New: {result['current_ip']}")
                    else:
                        print(f"[{datetime.now()}] IP unchanged: {result['current_ip']}")

                except Exception as e:
                    print(f"[{datetime.now()}] Error: {e}", file=sys.stderr)

                if max_runs is None or runs < max_runs:
                    time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped")


def main():
    parser = argparse.ArgumentParser(description="Track external IP address")
    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Update command
    subparsers.add_parser("update", help="Update IP once")

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor IP continuously")
    monitor_parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300)"
    )

    # Get command
    subparsers.add_parser("get", help="Get stored IP data")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    tracker = IPTracker(args.url, args.token)

    if args.command == "update":
        print("Checking IP address...")
        result = tracker.update_ip()

        print(f"Current IP: {result['current_ip']}")
        if result['changed']:
            print(f"Previous IP: {result['previous_ip']}")
            print("✓ IP has changed - updated in store")
        else:
            print("✓ IP unchanged")

    elif args.command == "get":
        data = tracker.get_stored_ip()
        if data:
            print(f"Stored IP data:")
            print(json.dumps(data, indent=2))
        else:
            print("No data stored yet")

    elif args.command == "monitor":
        tracker.monitor(interval=args.interval)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
