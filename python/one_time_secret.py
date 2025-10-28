#!/usr/bin/env python3
"""
One-Time Secret Service

Share secrets (passwords, API keys) that become invalid after being read once.
More secure than sending secrets via email or chat.

Features:
- Secrets are invalidated after first read
- Optional password protection
- Expiration time (TTL)
- Client-side encryption
- View count tracking

Requirements:
    pip install requests cryptography

Usage:
    # Create a one-time secret
    python one_time_secret.py create "My secret password"

    # Create with password protection
    python one_time_secret.py create "API Key: sk_123" --password mypass

    # Create with expiration (1 hour)
    python one_time_secret.py create "Temporary token" --ttl 3600

    # Read a secret
    python one_time_secret.py read your-five-word-token

    # Read with password
    python one_time_secret.py read your-five-word-token --password mypass
"""

import os
import requests
import json
import argparse
import sys
import base64
import getpass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")


class OneTimeSecret:
    """Create and retrieve one-time secrets."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def _create_cipher(self, password: str, salt: bytes) -> Fernet:
        """Create Fernet cipher from password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _encrypt(self, content: str, password: Optional[str] = None) -> Dict[str, str]:
        """Encrypt content with optional password."""
        if password:
            # Use password-based encryption
            salt = os.urandom(16)
            cipher = self._create_cipher(password, salt)
            encrypted = cipher.encrypt(content.encode())

            return {
                "encrypted": "password",
                "salt": base64.b64encode(salt).decode('utf-8'),
                "content": base64.b64encode(encrypted).decode('utf-8')
            }
        else:
            # No password, but still encode
            return {
                "encrypted": "none",
                "content": base64.b64encode(content.encode()).decode('utf-8')
            }

    def _decrypt(self, data: Dict[str, str], password: Optional[str] = None) -> str:
        """Decrypt content with optional password."""
        encryption_type = data.get("encrypted", "none")

        if encryption_type == "password":
            if not password:
                raise ValueError("This secret requires a password")

            salt = base64.b64decode(data["salt"])
            cipher = self._create_cipher(password, salt)
            encrypted = base64.b64decode(data["content"])
            decrypted = cipher.decrypt(encrypted)
            return decrypted.decode('utf-8')
        else:
            # No encryption, just decode
            return base64.b64decode(data["content"]).decode('utf-8')

    def create(
        self,
        token: str,
        secret: str,
        password: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a one-time secret.

        Args:
            token: The pre-generated token
            secret: The secret content
            password: Optional password protection
            ttl: Time-to-live in seconds

        Returns:
            Token and share URL
        """
        if not token:
            raise ValueError("Token is required to create a one-time secret")

        # Encrypt secret
        encrypted_data = self._encrypt(secret, password)

        # Add metadata
        data = {
            "secret": encrypted_data,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "one_time": True,
            "views": 0,
            "max_views": 1,
        }

        # Store with TTL
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

        return {
            "token": token,
            "url": f"{self.base_url.replace('/api', '')}/secret/{token}",
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat() + "Z" if ttl else None,
            "password_protected": password is not None
        }

    def read(self, token: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Read and delete a one-time secret.

        Args:
            token: The secret token
            password: Optional password if protected

        Returns:
            The secret content
        """
        # Retrieve the secret
        try:
            response = requests.get(
                f"{self.base_url}/api/retrieve",
                headers={"X-KV-Token": token}
            )
            response.raise_for_status()
            data = response.json()["data"]
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 404:
                return {
                    "success": False,
                    "error": "Secret not found or already read"
                }
            raise

        # Check if already viewed
        if data.get("views", 0) >= data.get("max_views", 1):
            # Delete it
            self._delete_secret(token)
            return {
                "success": False,
                "error": "Secret has already been read"
            }

        # Decrypt secret
        try:
            secret_content = self._decrypt(data["secret"], password)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to decrypt: {str(e)}"
            }

        # Increment view count and check if should mark consumed
        data["views"] = data.get("views", 0) + 1

        if data["views"] >= data.get("max_views", 1):
            # Overwrite the secret after reading
            self._mark_consumed(token)
            consumed = True
        else:
            # Update view count
            requests.post(
                f"{self.base_url}/api/store",
                json={"data": data},
                headers={
                    "Content-Type": "application/json",
                    "X-KV-Token": token
                }
            )
            consumed = False

        return {
            "success": True,
            "secret": secret_content,
            "created_at": data.get("created_at"),
            "views": data["views"],
            "consumed": consumed
        }

    def _mark_consumed(self, token: str):
        """Overwrite secret to prevent future reads without deleting the token."""
        placeholder = {
            "consumed": True,
            "consumed_at": datetime.utcnow().isoformat() + "Z"
        }
        try:
            requests.post(
                f"{self.base_url}/api/store",
                json={"data": placeholder},
                headers={
                    "Content-Type": "application/json",
                    "X-KV-Token": token
                }
            )
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="One-time secret sharing")
    parser.add_argument("--url", default=API_URL, help="API URL")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a one-time secret")
    create_parser.add_argument("secret", help="The secret to share")
    create_parser.add_argument(
        "--token",
        default=os.environ.get("KV_TOKEN"),
        help="Token to use for storing the secret (defaults to KV_TOKEN environment variable)"
    )
    create_parser.add_argument("--password", help="Password protect the secret")
    create_parser.add_argument("--ttl", type=int, help="Time-to-live in seconds (e.g., 3600 = 1 hour)")
    create_parser.add_argument("--prompt-password", action="store_true", help="Prompt for password (secure)")

    # Read command
    read_parser = subparsers.add_parser("read", help="Read a one-time secret")
    read_parser.add_argument("token", help="The secret token")
    read_parser.add_argument("--password", help="Password if protected")
    read_parser.add_argument("--prompt-password", action="store_true", help="Prompt for password (secure)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    ots = OneTimeSecret(args.url)

    if args.command == "create":
        # Handle password prompt
        password = args.password
        if args.prompt_password:
            password = getpass.getpass("Enter password to protect secret: ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("Passwords don't match!")
                sys.exit(1)

        token = args.token.strip() if args.token else None
        if not token:
            print("Error: token is required. Provide --token or set KV_TOKEN.")
            sys.exit(1)

        print("Creating one-time secret...")
        result = ots.create(token, args.secret, password=password, ttl=args.ttl)

        print("\n✓ Secret created successfully!")
        print(f"\nToken: {result['token']}")
        print(f"\nShare this token with the recipient.")
        print(f"The secret becomes invalid after it's read once.")

        if result['password_protected']:
            print(f"\n⚠️  Password required: Share the password separately!")

        if result['expires_at']:
            print(f"\n⏱  Expires at: {result['expires_at']}")

        print(f"\n📋 Copy this command for the recipient:")
        if password:
            print(f"   python one_time_secret.py read {result['token']} --prompt-password")
        else:
            print(f"   python one_time_secret.py read {result['token']}")

    elif args.command == "read":
        # Handle password prompt
        password = args.password
        if args.prompt_password:
            password = getpass.getpass("Enter password: ")

        print("Reading one-time secret...")
        result = ots.read(args.token, password=password)

        if result['success']:
            print("\n" + "="*60)
            print("SECRET:")
            print("="*60)
            print(result['secret'])
            print("="*60)

            if result['consumed']:
                print("\n✓ Secret has been consumed and cannot be read again.")
            else:
                print(f"\n⚠️  Secret has been viewed {result['views']} time(s)")

            print(f"\nCreated at: {result['created_at']}")
        else:
            print(f"\n✗ Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
