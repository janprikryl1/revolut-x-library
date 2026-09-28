"""Unit tests for the revolut_x._auth module."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from revolut_x._auth import (
    build_signature_message,
    load_private_key,
    sign_request,
)
from revolut_x.exceptions import AuthenticationError


def test_build_signature_message_basic() -> None:
    """Verify signature message format with timestamp, GET method, and path."""
    timestamp = "1710000000000"
    method = "GET"
    path = "/api/1.0/orders"

    message = build_signature_message(
        timestamp_ms=timestamp,
        method=method,
        path=path,
    )

    assert message == f"{timestamp}{method}{path}"
    assert message == "1710000000000GET/api/1.0/orders"

    # Verify that lowercase method is normalized to uppercase
    message_lower = build_signature_message(
        timestamp_ms=timestamp,
        method="get",
        path=path,
    )
    assert message_lower == "1710000000000GET/api/1.0/orders"


def test_build_signature_message_with_params() -> None:
    """Verify parameters are sorted alphabetically and URL-encoded."""
    timestamp = "1710000000000"
    method = "GET"
    path = "/api/1.0/orders"
    params = {
        "symbol": "BTC/EUR",
        "limit": 50,
        "after": "cursor_123",
        "empty_val": None,
    }

    message = build_signature_message(
        timestamp_ms=timestamp,
        method=method,
        path=path,
        params=params,
    )

    # Sorted non-None params:
    # 1. after=cursor_123
    # 2. limit=50
    # 3. symbol=BTC%2FEUR
    expected_query = "after=cursor_123&limit=50&symbol=BTC%2FEUR"
    assert message == f"1710000000000GET/api/1.0/orders{expected_query}"
    assert "empty_val" not in message


def test_build_signature_message_with_json_body() -> None:
    """Verify dictionary body is serialized as minified JSON without spaces."""
    timestamp = "1710000000000"
    method = "POST"
    path = "/api/1.0/orders"
    body = {
        "client_order_id": "4b68e984-6014-4112-9c3f-4e0730d43f07",
        "symbol": "BTC-EUR",
        "side": "buy",
        "order_configuration": {
            "market": {
                "quote_size": "50.00",
            }
        },
    }

    message = build_signature_message(
        timestamp_ms=timestamp,
        method=method,
        path=path,
        body=body,
    )

    expected_body = json.dumps(body, separators=(",", ":"))
    expected_message = f"1710000000000POST/api/1.0/orders{expected_body}"

    assert message == expected_message
    # Minified JSON should not contain spacing after delimiters
    assert ": " not in message
    assert ", " not in message


def test_build_signature_message_path_normalization() -> None:
    """Verify '/api' prefix is automatically prepended if missing."""
    timestamp = "1710000000000"
    method = "GET"

    message_missing_prefix = build_signature_message(
        timestamp_ms=timestamp,
        method=method,
        path="/1.0/orders",
    )
    message_with_prefix = build_signature_message(
        timestamp_ms=timestamp,
        method=method,
        path="/api/1.0/orders",
    )

    assert message_missing_prefix == "1710000000000GET/api/1.0/orders"
    assert message_missing_prefix == message_with_prefix


def test_load_private_key_file_not_found(tmp_path: Path) -> None:
    """Verify AuthenticationError with helpful message when private key file does not exist."""
    non_existent = tmp_path / "missing_private_key.pem"

    with pytest.raises(AuthenticationError) as exc_info:
        load_private_key(non_existent)

    error_msg = str(exc_info.value)
    assert "not found" in error_msg.lower()
    assert str(non_existent) in error_msg


def test_load_private_key_invalid_format() -> None:
    """Verify AuthenticationError when PEM data is corrupted or is not an Ed25519 key."""
    # Test completely invalid PEM bytes
    bad_data = b"-----BEGIN PRIVATE KEY-----\nNOT_BASE64\n-----END PRIVATE KEY-----"
    with pytest.raises(AuthenticationError) as exc_info:
        load_private_key(bad_data)

    assert "invalid private key format" in str(exc_info.value).lower()

    # Test valid PEM of wrong key type (RSA instead of Ed25519)
    rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    rsa_pem = rsa_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with pytest.raises(AuthenticationError) as exc_info_rsa:
        load_private_key(rsa_pem)

    assert "not an ed25519" in str(exc_info_rsa.value).lower()


def test_sign_request_returns_correct_headers() -> None:
    """Generate in-memory Ed25519 key pair, sign request, and verify headers and signature."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    api_key = "test-api-key-xyz"
    method = "POST"
    path = "/api/1.0/orders"
    body = {"symbol": "BTC-EUR", "side": "buy"}

    headers = sign_request(
        api_key=api_key,
        private_key=private_key,
        method=method,
        path=path,
        body=body,
    )

    # 1. Verify all three authentication headers are present
    assert "X-Revx-API-Key" in headers
    assert "X-Revx-Timestamp" in headers
    assert "X-Revx-Signature" in headers
    assert headers["Content-Type"] == "application/json"

    assert headers["X-Revx-API-Key"] == api_key
    assert headers["X-Revx-Timestamp"].isdigit()

    # 2. Verify signature is valid Base64 and decodes to 64 bytes (Ed25519 signature size)
    sig_b64 = headers["X-Revx-Signature"]
    sig_bytes = base64.b64decode(sig_b64)
    assert len(sig_bytes) == 64

    # 3. Mathematically verify signature with public key
    expected_message = build_signature_message(
        timestamp_ms=headers["X-Revx-Timestamp"],
        method=method,
        path=path,
        body=body,
    )
    # This will raise InvalidSignature exception if signature is invalid
    public_key.verify(sig_bytes, expected_message.encode("utf-8"))
