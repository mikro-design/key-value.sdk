"""Key-Value client implementation."""

import requests
from typing import Dict, Any, Optional, List
from .exceptions import (
    KeyValueError,
    RateLimitError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


class KeyValueClient:
    """
    Python client for Key-Value store API.

    Example:
        >>> client = KeyValueClient(token="word-word-word-word-word")
        >>> client.store({"temperature": 23.5})
        >>> data = client.retrieve()
    """

    def __init__(
        self,
        base_url: str = "https://key-value.co",
        token: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize Key-Value client.

        Args:
            base_url: API base URL (default: https://key-value.co)
            token: Default token for requests
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def set_token(self, token: str) -> None:
        """Set the default token for subsequent requests."""
        self.token = token

    def get_token(self) -> Optional[str]:
        """Get the current default token."""
        return self.token

    def generate(self, turnstile_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a new 5-word memorable token.

        Args:
            turnstile_token: Optional Cloudflare Turnstile token for bot protection

        Returns:
            dict: Response with 'token' field

        Example:
            >>> result = client.generate()
            >>> print(result['token'])
            'word-word-word-word-word'
        """
        payload = {}
        if turnstile_token:
            payload["turnstileToken"] = turnstile_token

        return self._request("POST", "/api/generate", json=payload, skip_token=True)

    def store(
        self,
        data: Any,
        token: Optional[str] = None,
        ttl: Optional[int] = None,
        schema: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Store JSON data with a token.

        Args:
            data: JSON-serializable data to store
            token: Token to use (defaults to client.token)
            ttl: Optional time-to-live in seconds (max 30 days)
            schema: Optional JSON schema for validation

        Returns:
            dict: Response with size, version, updated_at, etc.

        Raises:
            KeyValueError: If token is missing or request fails

        Example:
            >>> result = client.store({"temperature": 23.5}, ttl=3600)
            >>> print(f"Version: {result['version']}")
        """
        auth_token = token or self.token
        if not auth_token:
            raise KeyValueError("Token is required for store operation")

        payload = {"data": data}
        if ttl is not None:
            payload["ttl"] = ttl
        if schema is not None:
            payload["schema"] = schema

        return self._request(
            "POST", "/api/store", json=payload, headers={"X-KV-Token": auth_token}
        )

    def retrieve(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve data for a token.

        Args:
            token: Token to use (defaults to client.token)

        Returns:
            dict: Response with 'data', 'version', 'updated_at', 'expires_at'

        Raises:
            KeyValueError: If token is missing
            NotFoundError: If token has no data

        Example:
            >>> result = client.retrieve()
            >>> data = result['data']
            >>> version = result['version']
        """
        auth_token = token or self.token
        if not auth_token:
            raise KeyValueError("Token is required for retrieve operation")

        return self._request("GET", "/api/retrieve", headers={"X-KV-Token": auth_token})

    def delete(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete data for a token.

        Args:
            token: Token to use (defaults to client.token)

        Returns:
            dict: Success response

        Raises:
            KeyValueError: If token is missing
        """
        auth_token = token or self.token
        if not auth_token:
            raise KeyValueError("Token is required for delete operation")

        return self._request(
            "DELETE", "/api/delete", headers={"X-KV-Token": auth_token}
        )

    def patch(
        self,
        version: int,
        patch: Dict[str, Any],
        token: Optional[str] = None,
        ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Apply atomic partial updates with optimistic concurrency.

        Args:
            version: Current version for conflict detection
            patch: Operations dict with 'set' and/or 'remove' keys
            token: Token to use (defaults to client.token)
            ttl: Optional TTL update (None to clear expiry)

        Returns:
            dict: Response with new version and updated data

        Raises:
            ConflictError: If version mismatch (HTTP 409)

        Example:
            >>> result = client.patch(
            ...     version=5,
            ...     patch={
            ...         "set": {"profile.name": "Alice", "count": 42},
            ...         "remove": ["old_field"]
            ...     }
            ... )
            >>> new_version = result['version']
        """
        auth_token = token or self.token
        if not auth_token:
            raise KeyValueError("Token is required for patch operation")

        payload = {"version": version, "patch": patch}
        if ttl is not None:
            payload["ttl"] = ttl

        return self._request(
            "PATCH", "/api/store", json=payload, headers={"X-KV-Token": auth_token}
        )

    def history(
        self,
        token: Optional[str] = None,
        limit: int = 50,
        before: Optional[int] = None,
        since: Optional[str] = None,
        type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Query time-series event history for a token.

        Args:
            token: Token to use (defaults to client.token)
            limit: Max events to return (default: 50, max: 200)
            before: Return events with seq < this value (pagination)
            since: Return events created on or after this ISO timestamp
            type: Filter by classified event type

        Returns:
            dict: Response with 'events' list and 'pagination' info

        Example:
            >>> history = client.history(limit=100, since="2025-01-01T00:00:00Z")
            >>> for event in history['events']:
            ...     print(f"Seq {event['seq']}: {event['numeric_value']}")
        """
        auth_token = token or self.token
        if not auth_token:
            raise KeyValueError("Token is required for history operation")

        params = {"limit": limit}
        if before is not None:
            params["before"] = before
        if since is not None:
            params["since"] = since
        if type is not None:
            params["type"] = type

        return self._request(
            "GET", "/api/history", params=params, headers={"X-KV-Token": auth_token}
        )

    def batch(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multiple operations in a single request.

        Args:
            operations: List of operation dicts (max 100)
                Each operation must have:
                - action: 'store' | 'retrieve' | 'delete' | 'patch'
                - token: str
                - data: Any (for store)
                - ttl: int (optional, for store)
                - patch: dict (for patch)
                - version: int (for patch)

        Returns:
            dict: Response with 'results' list and 'summary' stats

        Raises:
            KeyValueError: If operations list is invalid

        Example:
            >>> result = client.batch([
            ...     {
            ...         "action": "store",
            ...         "token": "token-1",
            ...         "data": {"sensor": "temp-1", "value": 23.5}
            ...     },
            ...     {
            ...         "action": "retrieve",
            ...         "token": "token-2"
            ...     },
            ...     {
            ...         "action": "delete",
            ...         "token": "token-3"
            ...     }
            ... ])
            >>> print(f"Success rate: {result['summary']['successRate']}")
            >>> for res in result['results']:
            ...     if res['success']:
            ...         print(f"✓ {res['action']} succeeded")
            ...     else:
            ...         print(f"✗ {res['action']} failed: {res['error']}")
        """
        if not operations:
            raise KeyValueError("At least one operation is required")
        if len(operations) > 100:
            raise KeyValueError("Maximum 100 operations per batch request")

        return self._request(
            "POST", "/api/batch", json={"operations": operations}, skip_token=True
        )

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        skip_token: bool = False,
    ) -> Dict[str, Any]:
        """Internal request handler with error handling."""
        url = f"{self.base_url}{path}"
        req_headers = {"Content-Type": "application/json"}

        if headers:
            req_headers.update(headers)

        try:
            response = requests.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=req_headers,
                timeout=self.timeout,
            )

            # Parse JSON response
            try:
                data = response.json()
            except ValueError:
                data = {"error": response.text or "Invalid JSON response"}

            # Handle HTTP errors
            if not response.ok:
                error_msg = data.get("error", f"HTTP {response.status_code}")

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    raise RateLimitError(
                        error_msg, retry_after=int(retry_after) if retry_after else None
                    )
                elif response.status_code == 409:
                    raise ConflictError(error_msg)
                elif response.status_code == 404:
                    raise NotFoundError(error_msg)
                elif response.status_code == 400:
                    errors = data.get("validationErrors") or data.get("details")
                    raise ValidationError(error_msg, errors=errors)
                else:
                    raise KeyValueError(error_msg, response.status_code, data)

            return data

        except requests.exceptions.Timeout:
            raise KeyValueError(f"Request timeout after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise KeyValueError(f"Request failed: {str(e)}")
