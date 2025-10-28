"""
Key-Value Python Client

Official Python client for Key-Value store with memorable 5-word tokens.
"""

from .client import KeyValueClient
from .exceptions import KeyValueError, RateLimitError, ConflictError

__version__ = "0.1.0"
__all__ = ["KeyValueClient", "KeyValueError", "RateLimitError", "ConflictError"]
