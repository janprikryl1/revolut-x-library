"""Custom exceptions for the revolut-x-python library.

Exception hierarchy::

    RevolutXError (base)
    ├── AuthenticationError   — missing/invalid API key or private key
    ├── RateLimitError        — HTTP 429, retry after N seconds
    ├── ApiError              — any non-2xx API response
    ├── OrderValidationError  — payload violates exchange rules
    └── NetworkError          — connection timeout, DNS failure, etc.

All exceptions inherit from :class:`RevolutXError`, so you can catch them all
with a single ``except RevolutXError`` block, or handle each type individually.
"""

from __future__ import annotations

from typing import Any


class RevolutXError(Exception):
    """Base exception for all errors raised by the revolut-x-python library.

    You can catch this to handle any library error generically::

        try:
            client.get_ticker("BTC-EUR")
        except RevolutXError as exc:
            logging.error("Revolut X error: %s", exc)
    """


class AuthenticationError(RevolutXError):
    """Raised when authentication is missing, misconfigured, or rejected.

    Common causes:

    * ``api_key`` was not provided when creating :class:`RevolutXClient`.
    * The private key file does not exist or has an invalid format.
    * The API returned HTTP 401 or 403 (expired key, wrong signature, …).

    Attributes:
        hint: A human-readable suggestion on how to fix the problem.
    """

    def __init__(self, message: str, *, hint: str | None = None) -> None:
        self.hint = hint
        full = message
        if hint:
            full = f"{message}\n  Hint: {hint}"
        super().__init__(full)


class RateLimitError(RevolutXError):
    """Raised when the Revolut X API returns HTTP 429 (Too Many Requests).

    The library retries automatically up to ``max_retries`` times.  This
    exception is raised only when all retries have been exhausted.

    Attributes:
        retry_after_seconds: Suggested wait time (from the ``Retry-After``
            header), in seconds.  May be ``None`` if the header was absent.
        endpoint: The API endpoint that triggered the rate limit.
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after_seconds: float | None = None,
        endpoint: str | None = None,
    ) -> None:
        self.retry_after_seconds = retry_after_seconds
        self.endpoint = endpoint
        super().__init__(message)


class ApiError(RevolutXError):
    """Raised when the Revolut X API returns a non-2xx HTTP status code.

    This covers client errors (4xx) and server errors (5xx) that are not
    authentication (401/403) or rate-limit (429) related.

    Attributes:
        status_code: The HTTP status code returned by the API (e.g. 400, 404, 500).
        response_body: The parsed JSON response body, or raw text if parsing failed.
        endpoint: The API endpoint that was called (e.g. ``POST /api/1.0/orders``).
        method: The HTTP method used (e.g. ``GET``, ``POST``).
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response_body: Any = None,
        endpoint: str = "",
        method: str = "",
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        self.endpoint = endpoint
        self.method = method
        super().__init__(message)


class OrderValidationError(RevolutXError, ValueError):
    """Raised when an order payload violates exchange rules before submission.

    This is a **client-side** validation — the order is not sent to the
    exchange.  Fix the payload and try again.

    Attributes:
        errors: A list of human-readable strings describing each violated rule.

    Example::

        try:
            client.place_market_order("BTC-EUR", OrderSide.BUY, quote_size="0.01")
        except OrderValidationError as exc:
            for err in exc.errors:
                print(f"  - {err}")
    """

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            details = "\n".join(f"  - {e}" for e in self.errors)
            full = f"{message}\n{details}"
        else:
            full = message
        super().__init__(full)


class NetworkError(RevolutXError):
    """Raised when a network-level error prevents the request from completing.

    This wraps connection timeouts, DNS resolution failures, refused
    connections, and other transport-layer errors.

    Attributes:
        original_error: The underlying :class:`requests.RequestException`
            (or similar) that caused this error.
    """

    def __init__(self, message: str, *, original_error: Exception | None = None) -> None:
        self.original_error = original_error
        super().__init__(message)
