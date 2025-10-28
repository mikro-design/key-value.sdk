"""Custom exceptions for the Key-Value client."""


class KeyValueError(Exception):
    """Base exception for Key-Value client errors."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RateLimitError(KeyValueError):
    """Raised when rate limit is exceeded (HTTP 429)."""

    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ConflictError(KeyValueError):
    """Raised when version conflict occurs in PATCH (HTTP 409)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class NotFoundError(KeyValueError):
    """Raised when token/resource not found (HTTP 404)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ValidationError(KeyValueError):
    """Raised when request validation fails (HTTP 400)."""

    def __init__(self, message: str, errors: list = None):
        super().__init__(message, status_code=400)
        self.errors = errors or []
