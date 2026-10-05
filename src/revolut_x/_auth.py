"""Internal module for Ed25519 authentication for Revolut X."""

from __future__ import annotations
import base64
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from revolut_x.exceptions import AuthenticationError


def load_private_key(source: str | Path | bytes) -> Ed25519PrivateKey:
    """Load an Ed25519 private key from a file or raw PEM bytes.

    Args:
        source: The path to the PEM file (str or Path),
            or the raw PEM data (bytes).

    Returns:
        Ed25519PrivateKey: The loaded Ed25519 private key.

    Raises:
        AuthenticationError: If the file is not found, or the key format is invalid.
    """

    if isinstance(source, bytes):
        pem_data = source
    else:
        path = Path(source)
        if not path.is_file():
            raise AuthenticationError(f"Private key file not found at: {path}")
        try:
            pem_data = path.read_bytes()
        except OSError as e:
            raise AuthenticationError(f"Failed to read private key file at {path}: {e}")

    try:
        private_key = serialization.load_pem_private_key(pem_data, password=None)
        if not isinstance(private_key, Ed25519PrivateKey):
            raise AuthenticationError("The provided key is not an Ed25519 private key.")
        return private_key
    except ValueError as e:
        raise AuthenticationError(f"Invalid private key format: {e}")
    except Exception as e:
        raise AuthenticationError(f"Failed to load private key: {e}")


def build_signature_message(
    timestamp_ms: str,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: Any | None = None
) -> str:
    """Build the exact signature message string for Revolut X.

    The format is: {timestamp}{METHOD}{path}{query_string}{body}.

    Args:
        timestamp_ms: The current timestamp in milliseconds.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The request path, which must start with '/api'.
        params: Query parameters to include.
        body: The request body. Can be a dict/list (will be minified JSON)
            or a raw string.

    Returns:
        str: The constructed message string to be signed.
    """
    method_upper = method.upper()
    
    normalized_path = path if path.startswith("/api") else f"/api{path}"
    
    query_str = ""
    if params:
        clean_params = [(k, str(v)) for k, v in sorted(params.items()) if v is not None]
        query_str = urlencode(clean_params)
        
    body_str = ""
    if body is not None:
        if isinstance(body, (dict, list)):
            body_str = json.dumps(body, separators=(",", ":"))
        elif isinstance(body, str):
            body_str = body
            
    return f"{timestamp_ms}{method_upper}{normalized_path}{query_str}{body_str}"


def sign_request(
    api_key: str,
    private_key: Ed25519PrivateKey,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: Any | None = None
) -> dict[str, str]:
    """Sign a request and return the necessary authentication headers.

    Args:
        api_key: The Revolut X API key.
        private_key: The loaded Ed25519 private key.
        method: The HTTP method.
        path: The request path.
        params: The query parameters.
        body: The request body.

    Returns:
        A dictionary containing the authentication headers
            (X-Revx-API-Key, X-Revx-Timestamp, X-Revx-Signature) and Content-Type
            if a body is provided.
    """
    timestamp_ms = str(int(time.time() * 1000))
    
    message = build_signature_message(
        timestamp_ms=timestamp_ms,
        method=method,
        path=path,
        params=params,
        body=body
    )
    
    signature_bytes = private_key.sign(message.encode("utf-8"))
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")
    
    headers = {
        "X-Revx-API-Key": api_key,
        "X-Revx-Timestamp": timestamp_ms,
        "X-Revx-Signature": signature_b64
    }
    
    if body is not None:
        headers["Content-Type"] = "application/json"
        
    return headers
