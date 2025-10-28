#!/usr/bin/env python3
"""
Webhook Receiver

Catch and store webhook payloads from external services (GitHub, Stripe, etc.)
Useful for debugging webhooks or building integrations without a server.

Features:
- Generate unique webhook URLs
- Catch and store webhook payloads
- View recent webhooks
- Filter by event type
- Works with any webhook provider

Requirements:
    pip install requests flask

Usage:
    # Generate a webhook URL
    python webhook_receiver.py --token YOUR-TOKEN generate

    # Start local server to receive webhooks (for testing)
    python webhook_receiver.py --token YOUR-TOKEN serve --port 5000

    # View received webhooks
    python webhook_receiver.py --token YOUR-TOKEN list

    # View specific webhook
    python webhook_receiver.py --token YOUR-TOKEN view 0

    # Send test webhook (for testing)
    python webhook_receiver.py --token YOUR-TOKEN test
"""

import os
import requests
import json
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from flask import Flask, request, jsonify
except ImportError:
    Flask = None

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")
MAX_WEBHOOKS = 50  # Keep last 50 webhooks


class WebhookReceiver:
    """Receive and store webhooks."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token

    def add_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Store a webhook payload.

        Args:
            payload: Webhook payload
            headers: Request headers

        Returns:
            Result
        """
        # Get existing data
        data = self._get_data()

        # Create webhook entry
        webhook = {
            "id": data.get("webhook_count", 0),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload,
            "headers": dict(headers),
        }

        # Try to detect event type from common header names
        event_type = (
            headers.get("X-GitHub-Event") or
            headers.get("X-Event-Type") or
            headers.get("X-Webhook-Event") or
            payload.get("type") or
            payload.get("event") or
            "unknown"
        )
        webhook["event_type"] = event_type

        # Add to history
        history = data.get("webhooks", [])
        history.append(webhook)

        # Keep only last MAX_WEBHOOKS
        if len(history) > MAX_WEBHOOKS:
            history = history[-MAX_WEBHOOKS:]

        # Update data
        data["webhooks"] = history
        data["webhook_count"] = data.get("webhook_count", 0) + 1
        data["last_webhook"] = webhook["timestamp"]

        # Store
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
            "webhook_id": webhook["id"],
            "event_type": event_type
        }

    def list_webhooks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List recent webhooks."""
        data = self._get_data()
        webhooks = data.get("webhooks", [])
        if limit:
            return webhooks[-limit:]
        return webhooks

    def get_webhook(self, webhook_id: int) -> Optional[Dict[str, Any]]:
        """Get specific webhook by ID."""
        webhooks = self.list_webhooks()
        for webhook in webhooks:
            if webhook["id"] == webhook_id:
                return webhook
        return None

    def generate_url(self) -> str:
        """Generate webhook receiver URL."""
        # For now, return instructions to use the Flask server
        return f"http://localhost:5000/webhook/{self.token}"

    def serve(self, port: int = 5000):
        """Start Flask server to receive webhooks."""
        if Flask is None:
            print("Error: flask not installed. Install with: pip install flask")
            sys.exit(1)

        app = Flask(__name__)

        @app.route('/webhook/<token>', methods=['POST', 'GET', 'PUT', 'PATCH', 'DELETE'])
        def receive_webhook(token):
            if token != self.token:
                return jsonify({"error": "Invalid token"}), 401

            # Get payload
            if request.is_json:
                payload = request.json
            else:
                payload = {
                    "content_type": request.content_type,
                    "data": request.data.decode('utf-8', errors='ignore')
                }

            # Store webhook
            result = self.add_webhook(payload, request.headers)

            print(f"[{datetime.now()}] Received webhook #{result['webhook_id']} - {result['event_type']}")

            return jsonify({
                "success": True,
                "message": "Webhook received",
                "webhook_id": result["webhook_id"]
            })

        @app.route('/webhook/<token>/list', methods=['GET'])
        def list_webhooks_route(token):
            if token != self.token:
                return jsonify({"error": "Invalid token"}), 401

            webhooks = self.list_webhooks()
            return jsonify({
                "success": True,
                "count": len(webhooks),
                "webhooks": webhooks
            })

        @app.route('/')
        def index():
            return f"""
            <h1>Webhook Receiver</h1>
            <p>Webhook URL: <code>http://localhost:{port}/webhook/YOUR-TOKEN</code></p>
            <p>Status: Running ✓</p>
            """

        print(f"Starting webhook receiver on port {port}")
        print(f"\nWebhook URL: http://localhost:{port}/webhook/{self.token}")
        print(f"View webhooks: http://localhost:{port}/webhook/{self.token}/list")
        print("\nPress Ctrl+C to stop\n")

        try:
            app.run(host='0.0.0.0', port=port, debug=False)
        except KeyboardInterrupt:
            print("\nServer stopped")

    def send_test_webhook(self):
        """Send a test webhook."""
        payload = {
            "event": "test",
            "message": "This is a test webhook",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "user": "test_user",
                "action": "test_action"
            }
        }

        headers = {
            "X-Event-Type": "test",
            "User-Agent": "Webhook-Test/1.0"
        }

        result = self.add_webhook(payload, headers)
        return result

    def _get_data(self) -> Dict[str, Any]:
        """Get stored data."""
        try:
            response = requests.get(
                f"{self.base_url}/api/retrieve",
                headers={"X-KV-Token": self.token}
            )
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 404:
                return {}
            raise


def main():
    parser = argparse.ArgumentParser(description="Webhook receiver")
    parser.add_argument("--token", required=True, help="Key-value store token")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Generate command
    subparsers.add_parser("generate", help="Generate webhook URL")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start webhook receiver server")
    serve_parser.add_argument("--port", type=int, default=5000, help="Port (default: 5000)")

    # List command
    list_parser = subparsers.add_parser("list", help="List received webhooks")
    list_parser.add_argument("--limit", type=int, help="Limit results")

    # View command
    view_parser = subparsers.add_parser("view", help="View specific webhook")
    view_parser.add_argument("webhook_id", type=int, help="Webhook ID")

    # Test command
    subparsers.add_parser("test", help="Send test webhook")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    receiver = WebhookReceiver(args.url, args.token)

    if args.command == "generate":
        url = receiver.generate_url()
        print("Webhook receiver setup:")
        print("\n1. Start the receiver server:")
        print(f"   python webhook_receiver.py --token {args.token} serve")
        print("\n2. Expose to internet (using ngrok or similar):")
        print(f"   ngrok http 5000")
        print("\n3. Configure your webhook provider to send to:")
        print(f"   http://your-ngrok-url/webhook/{args.token}")
        print("\n4. View received webhooks:")
        print(f"   python webhook_receiver.py --token {args.token} list")

    elif args.command == "serve":
        receiver.serve(port=args.port)

    elif args.command == "list":
        webhooks = receiver.list_webhooks(limit=args.limit)

        if not webhooks:
            print("No webhooks received yet")
            return

        print(f"Received {len(webhooks)} webhook(s):\n")
        for webhook in webhooks:
            print(f"ID: {webhook['id']}")
            print(f"Time: {webhook['timestamp']}")
            print(f"Event: {webhook['event_type']}")
            print(f"Payload size: {len(json.dumps(webhook['payload']))} bytes")
            print("-" * 60)

    elif args.command == "view":
        webhook = receiver.get_webhook(args.webhook_id)

        if not webhook:
            print(f"Webhook #{args.webhook_id} not found")
            sys.exit(1)

        print(f"Webhook #{webhook['id']}")
        print(f"Time: {webhook['timestamp']}")
        print(f"Event: {webhook['event_type']}")
        print("\nHeaders:")
        print(json.dumps(webhook['headers'], indent=2))
        print("\nPayload:")
        print(json.dumps(webhook['payload'], indent=2))

    elif args.command == "test":
        result = receiver.send_test_webhook()
        print(f"✓ Test webhook sent (ID: {result['webhook_id']})")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
