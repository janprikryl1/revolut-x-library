"""Internal HTTP client module for Revolut X REST API requests."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from revolut_x._auth import sign_request
from revolut_x.exceptions import ApiError, AuthenticationError, NetworkError, RateLimitError

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP client handling authentication, headers, and rate limiting for Revolut X.

    Attributes:
        base_url (str): The base URL for the API.
        api_version (str): The API version string.
        api_key (str | None): The API key for authenticated requests.
        private_key (Ed25519PrivateKey | None): The private key for signing requests.
        request_delay (float): Minimum seconds between outgoing requests.
        timeout (int): Timeout in seconds for HTTP requests.
        max_retries (int): Maximum number of retry attempts for 429 and network errors.
        user_agent (str): User agent string for the requests.
    """

    def __init__(
        self,
        *,
        base_url: str = "https://revx.revolut.com/api",
        api_version: str = "1.0",
        api_key: str | None = None,
        private_key: Ed25519PrivateKey | None = None,
        request_delay: float = 0.85,
        timeout: int = 15,
        max_retries: int = 3,
        user_agent: str = "revolut-x-python/0.1.0",
    ):
        """Initialize the HTTP client.

        Args:
            base_url (str): The base URL for the API.
            api_version (str): The API version string.
            api_key (str | None): The API key for authenticated requests.
            private_key (Ed25519PrivateKey | None): The private key for signing requests.
            request_delay (float): Minimum seconds between outgoing requests.
            timeout (int): Timeout in seconds for HTTP requests.
            max_retries (int): Maximum number of retry attempts for 429 and network errors.
            user_agent (str): User agent string for the requests.
        """
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.api_key = api_key
        self.private_key = private_key
        self.request_delay = request_delay
        self.timeout = timeout
        self.max_retries = max_retries

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self._last_request_time = 0.0

    def _rate_limit_wait(self) -> None:
        """Enforce spacing between outgoing requests to avoid 429 Rate Limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self._last_request_time = time.time()

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        authenticated: bool = False,
    ) -> tuple[int, Any]:
        """Execute an HTTP request against the Revolut X API.

        Args:
            method (str): The HTTP method (GET, POST, etc.).
            endpoint (str): The API endpoint path (e.g., '/orders').
            params (dict[str, Any] | None): Optional query parameters.
            json_body (Any | None): Optional JSON body data.
            authenticated (bool): Whether the request requires authentication.

        Returns:
            tuple[int, Any]: A tuple containing the HTTP status code and the parsed response body
                (as a dict or list), or text if not parseable.

        Raises:
            AuthenticationError: If authentication is required but missing, or on 401/403.
            RateLimitError: If the maximum rate limit retries are exhausted (429).
            ApiError: For other 4xx or 5xx status codes.
            NetworkError: On fundamental network failures (e.g., connection errors).
        """
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        api_path = f"/api/{self.api_version}{endpoint}"
        full_url = f"{self.base_url}/{self.api_version}{endpoint}"

        headers: dict[str, str] = {}
        if authenticated:
            if not self.api_key or not self.private_key:
                raise AuthenticationError(
                    f"Authentication required for {endpoint}, but api_key or private_key is not configured. "
                    "Please initialize the client with both api_key and private_key."
                )
            
            auth_headers = sign_request(
                api_key=self.api_key,
                private_key=self.private_key,
                method=method,
                path=api_path,
                params=params,
                body=json_body
            )
            headers.update(auth_headers)

        body_kwargs: dict[str, Any] = {}
        if json_body is not None:
            body_kwargs["data"] = json.dumps(json_body, separators=(",", ":"))
            headers["Content-Type"] = "application/json"

        wait_sec: float | None = None
        for attempt in range(1, self.max_retries + 1):
            self._rate_limit_wait()
            try:
                response = self.session.request(
                    method=method.upper(),
                    url=full_url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                    **body_kwargs
                )
                
                status = response.status_code
                
                # Handle Rate Limiting (429)
                if status == 429:
                    if attempt == self.max_retries:
                        raise RateLimitError(
                            f"Rate limit exceeded for {method.upper()} {endpoint} after {self.max_retries} retries.",
                            retry_after_seconds=wait_sec,
                            endpoint=endpoint,
                        )
                    retry_after_str = response.headers.get("Retry-After", "2000")
                    try:
                        retry_after_ms = float(retry_after_str)
                        wait_sec = max(retry_after_ms / 1000.0, 1.0)
                    except ValueError:
                        wait_sec = 2.0
                    
                    wait_sec *= attempt
                    logger.warning(
                        "Rate limited on %s. Waiting %.2fs (attempt %d/%d).",
                        endpoint, wait_sec, attempt, self.max_retries
                    )
                    time.sleep(wait_sec)
                    continue

                try:
                    data = response.json()
                except Exception:
                    data = response.text

                # Handle other status codes
                if status in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed for {method.upper()} {endpoint} (HTTP {status}): {data}",
                        hint="Check that your API key is valid and the private key matches the registered public key.",
                    )
                elif not (200 <= status < 300):
                    raise ApiError(
                        f"Revolut X API returned HTTP {status} for {method.upper()} {endpoint}: {data}",
                        status_code=status,
                        response_body=data,
                        endpoint=endpoint,
                        method=method.upper(),
                    )

                return status, data

            except requests.RequestException as e:
                logger.error("Network error on %s %s: %s", method, full_url, e)
                if attempt == self.max_retries:
                    raise NetworkError(
                        f"Network error calling {method.upper()} {endpoint} after {self.max_retries} attempts: {e}",
                        original_error=e,
                    ) from e
                
                # Exponential backoff on network error
                time.sleep(1.0 * (2 ** (attempt - 1)))

        raise RateLimitError(f"Maximum retries ({self.max_retries}) exhausted for {endpoint}.")
