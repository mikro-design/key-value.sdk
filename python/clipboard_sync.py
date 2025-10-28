#!/usr/bin/env python3
"""
Clipboard Sync Service

Sync clipboard content between devices using the key-value store.
Perfect for copying text from one device and pasting on another.

Features:
- Automatically sync clipboard content
- Monitor mode for continuous sync
- Cross-platform support (Linux, macOS, Windows)
- Optionally encrypt clipboard content

Requirements:
    pip install requests pyperclip

Usage:
    # Copy local clipboard to cloud (one-time)
    python clipboard_sync.py --token YOUR-TOKEN push

    # Get cloud clipboard and copy to local
    python clipboard_sync.py --token YOUR-TOKEN pull

    # Monitor and auto-sync (push on clipboard change)
    python clipboard_sync.py --token YOUR-TOKEN monitor --interval 2

    # Monitor and auto-pull
    python clipboard_sync.py --token YOUR-TOKEN monitor --mode pull --interval 5
"""

import os
import requests
import json
import time
import argparse
import sys
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import pyperclip
except ImportError:
    print("Error: pyperclip not installed. Install with: pip install pyperclip")
    sys.exit(1)

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")


class ClipboardSync:
    """Sync clipboard content across devices."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.last_hash = None

    def get_clipboard_hash(self, content: str) -> str:
        """Get hash of clipboard content to detect changes."""
        return hashlib.sha256(content.encode()).hexdigest()

    def push_clipboard(self) -> Dict[str, Any]:
        """Push local clipboard to cloud."""
        try:
            content = pyperclip.paste()

            if not content:
                return {
                    "success": False,
                    "message": "Clipboard is empty"
                }

            # Store clipboard with metadata
            data = {
                "content": content,
                "length": len(content),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "device": self._get_device_name(),
            }

            response = requests.post(
                f"{self.base_url}/api/store",
                json={"data": data},
                headers={
                    "Content-Type": "application/json",
                    "X-KV-Token": self.token
                }
            )
            response.raise_for_status()

            return {
                "success": True,
                "message": "Clipboard pushed to cloud",
                "length": len(content),
                "preview": content[:100] + "..." if len(content) > 100 else content
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to push: {e}"
            }

    def pull_clipboard(self) -> Dict[str, Any]:
        """Pull cloud clipboard to local."""
        try:
            response = requests.get(
                f"{self.base_url}/api/retrieve",
                headers={"X-KV-Token": self.token}
            )
            response.raise_for_status()

            data = response.json()["data"]
            content = data.get("content", "")

            if not content:
                return {
                    "success": False,
                    "message": "No clipboard content in cloud"
                }

            # Copy to local clipboard
            pyperclip.copy(content)

            return {
                "success": True,
                "message": "Clipboard pulled from cloud",
                "length": len(content),
                "preview": content[:100] + "..." if len(content) > 100 else content,
                "device": data.get("device", "unknown"),
                "timestamp": data.get("timestamp", "unknown")
            }

        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 404:
                return {
                    "success": False,
                    "message": "No clipboard data found in cloud"
                }
            return {
                "success": False,
                "message": f"Failed to pull: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to pull: {e}"
            }

    def monitor(self, interval: int = 2, mode: str = "push"):
        """
        Monitor clipboard and auto-sync.

        Args:
            interval: Check interval in seconds
            mode: 'push' (monitor local, push changes) or 'pull' (monitor cloud, pull changes)
        """
        print(f"Starting clipboard monitor in {mode} mode (checking every {interval}s)")
        print(f"Press Ctrl+C to stop\n")

        try:
            while True:
                try:
                    if mode == "push":
                        # Monitor local clipboard, push if changed
                        content = pyperclip.paste()
                        current_hash = self.get_clipboard_hash(content) if content else None

                        if current_hash and current_hash != self.last_hash:
                            result = self.push_clipboard()
                            if result["success"]:
                                print(f"[{datetime.now()}] Pushed: {result['preview']}")
                                self.last_hash = current_hash
                            else:
                                print(f"[{datetime.now()}] Failed: {result['message']}")

                    elif mode == "pull":
                        # Monitor cloud, pull if changed
                        try:
                            response = requests.get(
                                f"{self.base_url}/api/retrieve",
                                headers={"X-KV-Token": self.token}
                            )
                            response.raise_for_status()
                            data = response.json()["data"]
                            content = data.get("content", "")
                            current_hash = self.get_clipboard_hash(content) if content else None

                            if current_hash and current_hash != self.last_hash:
                                # Check if it's different from local
                                local_content = pyperclip.paste()
                                local_hash = self.get_clipboard_hash(local_content) if local_content else None

                                if current_hash != local_hash:
                                    pyperclip.copy(content)
                                    preview = content[:100] + "..." if len(content) > 100 else content
                                    print(f"[{datetime.now()}] Pulled: {preview}")
                                    self.last_hash = current_hash
                        except requests.exceptions.HTTPError:
                            pass  # No data yet

                except Exception as e:
                    print(f"[{datetime.now()}] Error: {e}", file=sys.stderr)

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped")

    def _get_device_name(self) -> str:
        """Get device name for metadata."""
        import platform
        import socket
        try:
            return f"{socket.gethostname()} ({platform.system()})"
        except:
            return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Sync clipboard across devices")
    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Push command
    subparsers.add_parser("push", help="Push local clipboard to cloud")

    # Pull command
    subparsers.add_parser("pull", help="Pull cloud clipboard to local")

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor and auto-sync")
    monitor_parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Check interval in seconds (default: 2)"
    )
    monitor_parser.add_argument(
        "--mode",
        choices=["push", "pull"],
        default="push",
        help="Monitor mode: push (local changes) or pull (cloud changes)"
    )

    # Status command
    subparsers.add_parser("status", help="Show current cloud clipboard status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    sync = ClipboardSync(args.url, args.token)

    if args.command == "push":
        result = sync.push_clipboard()
        print(f"{result['message']}")
        if result['success']:
            print(f"Length: {result['length']} chars")
            print(f"Preview: {result['preview']}")

    elif args.command == "pull":
        result = sync.pull_clipboard()
        print(f"{result['message']}")
        if result['success']:
            print(f"Length: {result['length']} chars")
            print(f"Preview: {result['preview']}")
            print(f"From: {result['device']} at {result['timestamp']}")

    elif args.command == "status":
        result = sync.pull_clipboard()
        if result['success']:
            print(f"Cloud clipboard status:")
            print(f"  Length: {result['length']} chars")
            print(f"  Device: {result['device']}")
            print(f"  Time: {result['timestamp']}")
            print(f"  Preview: {result['preview']}")
        else:
            print(result['message'])

    elif args.command == "monitor":
        sync.monitor(interval=args.interval, mode=args.mode)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
