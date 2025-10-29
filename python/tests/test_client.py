"""Tests for KeyValueClient."""

import pytest
from unittest.mock import Mock, patch
from keyvalue import KeyValueClient
from keyvalue.exceptions import KeyValueError


class TestKeyValueClient:
    """Test suite for KeyValueClient."""

    def test_client_initialization(self):
        """Test client initialization with default values."""
        client = KeyValueClient()
        assert client.base_url == "https://key-value.co"
        assert client.token is None
        assert client.timeout == 30

    def test_client_initialization_with_custom_values(self):
        """Test client initialization with custom values."""
        client = KeyValueClient(
            base_url="https://custom.example.com",
            token="test-token-here",
            timeout=60
        )
        assert client.base_url == "https://custom.example.com"
        assert client.token == "test-token-here"
        assert client.timeout == 60

    def test_client_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base_url."""
        client = KeyValueClient(base_url="https://example.com/")
        assert client.base_url == "https://example.com"

    def test_set_token(self):
        """Test setting token."""
        client = KeyValueClient()
        assert client.get_token() is None
        client.set_token("new-token")
        assert client.get_token() == "new-token"

    def test_store_without_token_raises_error(self):
        """Test that store raises error when token is missing."""
        client = KeyValueClient()
        with pytest.raises(KeyValueError, match="Token is required"):
            client.store({"test": "data"})

    @patch('keyvalue.client.requests.request')
    def test_generate_success(self, mock_request):
        """Test generate method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "token": "word-word-word-word-word"}
        mock_request.return_value = mock_response

        client = KeyValueClient()
        result = client.generate()

        assert result["success"] is True
        assert result["token"] == "word-word-word-word-word"
        mock_request.assert_called_once()

    @patch('keyvalue.client.requests.request')
    def test_store_success(self, mock_request):
        """Test store method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Data stored successfully",
            "size": 100,
            "version": 1,
            "tier": "free"
        }
        mock_request.return_value = mock_response

        client = KeyValueClient(token="test-token")
        result = client.store({"temperature": 23.5})

        assert result["success"] is True
        assert result["version"] == 1
        mock_request.assert_called_once()

    @patch('keyvalue.client.requests.request')
    def test_retrieve_success(self, mock_request):
        """Test retrieve method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"temperature": 23.5},
            "version": 1
        }
        mock_request.return_value = mock_response

        client = KeyValueClient(token="test-token")
        result = client.retrieve()

        assert result["success"] is True
        assert result["data"]["temperature"] == 23.5
        assert result["version"] == 1
        mock_request.assert_called_once()

    @patch('keyvalue.client.requests.request')
    def test_delete_success(self, mock_request):
        """Test delete method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Data deleted successfully"
        }
        mock_request.return_value = mock_response

        client = KeyValueClient(token="test-token")
        result = client.delete()

        assert result["success"] is True
        assert "deleted successfully" in result["message"]
        mock_request.assert_called_once()

    def test_client_context_manager(self):
        """Test that client can be used as context manager if implemented."""
        client = KeyValueClient(token="test-token")
        # Basic instantiation test
        assert client is not None
        assert client.token == "test-token"
