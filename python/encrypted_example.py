#!/usr/bin/env python3
"""
Encrypted Key-Value Store Example

Demonstrates client-side encryption before storing sensitive data with a
user-provided token. The server stores encrypted data and cannot read the
contents without the password.

Requirements:
    pip install requests cryptography
"""

import argparse
import os
import requests
import json
import base64
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configuration
API_URL = os.environ.get("API_URL", "https://key-value.co")


class EncryptedKeyValueClient:
    """Client with automatic encryption/decryption."""

    def __init__(self, base_url: str, password: str):
        """
        Initialize client with encryption password.

        Args:
            base_url: API base URL
            password: Password used to derive encryption key
        """
        self.base_url = base_url.rstrip('/')
        self.cipher = self._create_cipher(password)

    def _create_cipher(self, password: str) -> Fernet:
        """Create Fernet cipher from password."""
        # Use a fixed salt for deterministic key derivation
        # In production, store salt separately and retrieve it
        salt = b'keyvalue-store-salt-change-this!'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _encrypt_data(self, data: Dict[Any, Any]) -> Dict[str, str]:
        """Encrypt data payload."""
        json_str = json.dumps(data)
        encrypted = self.cipher.encrypt(json_str.encode())
        return {
            "encrypted": True,
            "payload": base64.b64encode(encrypted).decode('utf-8')
        }

    def _decrypt_data(self, encrypted_data: Dict[str, str]) -> Dict[Any, Any]:
        """Decrypt data payload."""
        if not encrypted_data.get("encrypted"):
            raise ValueError("Data is not encrypted")

        payload = base64.b64decode(encrypted_data["payload"])
        decrypted = self.cipher.decrypt(payload)
        return json.loads(decrypted.decode())

    def store(self, token: str, data: Dict[Any, Any], ttl: Optional[int] = None) -> Dict:
        """
        Encrypt and store data.

        Args:
            token: The 5-word token
            data: JSON-serializable data to encrypt and store
            ttl: Optional time-to-live in seconds

        Returns:
            Response data with success status
        """
        encrypted_data = self._encrypt_data(data)

        payload = {
            "data": encrypted_data
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

    def retrieve(self, token: str) -> Dict[Any, Any]:
        """
        Retrieve and decrypt data.

        Args:
            token: The 5-word token

        Returns:
            The decrypted data
        """
        response = requests.get(
            f"{self.base_url}/api/retrieve",
            headers={"X-KV-Token": token}
        )
        response.raise_for_status()
        data = response.json()

        return self._decrypt_data(data['data'])


def main():
    """Demonstrate encrypted key-value operations."""
    parser = argparse.ArgumentParser(description="Encrypted key-value store example")
    parser.add_argument(
        "--token",
        default=os.environ.get("KV_TOKEN"),
        help="Token to use (defaults to KV_TOKEN environment variable)",
    )
    parser.add_argument(
        "--password",
        default="my-super-secret-password-123",
        help="Password used to derive the encryption key",
    )
    args = parser.parse_args()

    if not args.token:
        print("Error: token is required. Provide --token or set KV_TOKEN.")
        return

    password = args.password
    token = args.token.strip()

    client = EncryptedKeyValueClient(API_URL, password)

    print("=== Using Provided Token ===")
    print(f"Token: {token}")
    print(f"Encryption password: {password}")
    print("Keep both safe!\n")

    # Step 1: Store sensitive data (will be encrypted automatically)
    print("=== Storing Encrypted Data ===")
    sensitive_data = {
        "api_key": "sk_live_1234567890abcdef",
        "database_url": "postgresql://user:pass@host:5432/db",
        "secrets": {
            "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
            "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        },
        "credit_card": {
            "number": "4532-1234-5678-9010",
            "cvv": "123"
        }
    }

    result = client.store(token, sensitive_data)
    print(f"Store result: {json.dumps(result, indent=2)}")
    print("✓ Data encrypted and stored on server\n")

    # Step 2: Retrieve and decrypt
    print("=== Retrieving and Decrypting ===")
    retrieved = client.retrieve(token)
    print(f"Decrypted data: {json.dumps(retrieved, indent=2)}\n")

    # Verify
    assert retrieved == sensitive_data, "Data mismatch!"
    print("✓ Data successfully encrypted, stored, and decrypted!")

    # Step 3: Show what's actually stored on the server
    print("\n=== What the Server Sees ===")
    response = requests.get(
        f"{API_URL}/api/retrieve",
        headers={"X-KV-Token": token}
    )
    server_data = response.json()['data']
    print("Encrypted payload on server:")
    print(f"  - encrypted: {server_data['encrypted']}")
    print(f"  - payload: {server_data['payload'][:80]}...")
    print("\n✓ Server cannot read your data without the password!")

    # Step 4: Wrong password fails
    print("\n=== Testing Wrong Password ===")
    try:
        wrong_client = EncryptedKeyValueClient(API_URL, "wrong-password")
        wrong_client.retrieve(token)
        print("✗ Should have failed!")
    except Exception as e:
        print(f"✓ Decryption failed as expected: {type(e).__name__}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if e.response:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
