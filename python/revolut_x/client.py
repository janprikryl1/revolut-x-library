"""Main client for the Revolut X Crypto Exchange REST API.

This module provides :class:`RevolutXClient`, the single entry point for all
Revolut X API operations.  It combines public market data, order management,
and account endpoints into one unified interface.

Example — public data (no API key needed)::

    from revolut_x import RevolutXClient

    client = RevolutXClient()
    ticker = client.get_ticker("BTC-EUR")
    print(f"BTC price: {ticker['last_price']} EUR")

Example — trading (requires API key and private key)::

    from revolut_x import RevolutXClient, OrderSide

    client = RevolutXClient(
        api_key="Vw7fXD...",
        private_key_path="keys/private.pem",
    )
    order = client.place_market_order("BTC-EUR", OrderSide.BUY, quote_size="50.00")
    print(f"Order ID: {order['venue_order_id']}")
"""

from __future__ import annotations

import logging
from pathlib import Path

from revolut_x._auth import load_private_key
from revolut_x._http import HttpClient
from revolut_x.account import AccountMixin
from revolut_x.market import MarketMixin
from revolut_x.orders import OrdersMixin

logger = logging.getLogger(__name__)


class RevolutXClient(MarketMixin, OrdersMixin, AccountMixin):
    """Client for the Revolut X Crypto Exchange REST API.

    Provides complete access to:

    * **Public market data** (no API key needed): trading pair configuration,
      currency info, tickers, order book, OHLCV candles, and public trades.
    * **Order management** (API key required): place market/limit orders,
      cancel orders, inspect fills, view active and historical orders.
    * **Account data** (API key required): balances, transaction ledger,
      private trade history.

    Args:
        api_key: Your Revolut X API key.  Required only for authenticated
            endpoints (orders, balances, etc.).  Get it from your
            `Revolut X account settings <https://revx.revolut.com>`_.
        private_key_path: Path to your Ed25519 private key PEM file.
            Mutually exclusive with ``private_key_bytes``.
        private_key_bytes: Ed25519 private key as raw PEM bytes.
            Mutually exclusive with ``private_key_path``.
        base_url: API base URL (default: ``'https://revx.revolut.com/api'``).
            Change for sandbox/testing environments.
        api_version: API version string (default: ``'1.0'``).
        request_delay: Minimum seconds between HTTP requests to respect
            rate limits (default: ``0.85``).  The Revolut X public API
            allows 1 request per second.
        timeout: HTTP request timeout in seconds (default: ``15``).
        max_retries: Maximum retry attempts for rate-limited (429) or
            failed requests (default: ``3``).

    Raises:
        AuthenticationError: If ``private_key_path`` is provided but the
            file does not exist or contains an invalid key.

    Example::

        # Public data only — no credentials needed
        client = RevolutXClient()
        pairs = client.get_pairs()
        candles = client.get_candles("BTC-EUR", Interval.HOUR_1)

        # Full access — trading and account management
        client = RevolutXClient(
            api_key="your-api-key",
            private_key_path="/path/to/private.pem",
        )
        balances = client.get_balances()
        order = client.place_market_order("BTC-EUR", OrderSide.BUY, quote_size="50")
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        private_key_path: str | Path | None = None,
        private_key_bytes: bytes | None = None,
        base_url: str = "https://revx.revolut.com/api",
        api_version: str = "1.0",
        request_delay: float = 0.85,
        timeout: int = 15,
        max_retries: int = 3,
    ) -> None:
        # Load private key if credentials are provided
        private_key = None
        if private_key_path is not None:
            private_key = load_private_key(private_key_path)
            logger.info("Ed25519 private key loaded from %s", private_key_path)
        elif private_key_bytes is not None:
            private_key = load_private_key(private_key_bytes)
            logger.info("Ed25519 private key loaded from bytes")

        # Create the internal HTTP client shared by all mixins
        self._http = HttpClient(
            base_url=base_url,
            api_version=api_version,
            api_key=api_key,
            private_key=private_key,
            request_delay=request_delay,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Store for diagnostics
        self._api_key = api_key
        self._has_private_key = private_key is not None

    @property
    def is_authenticated(self) -> bool:
        """Whether the client has API key and private key configured.

        Returns:
            ``True`` if both ``api_key`` and a private key were provided,
            meaning authenticated endpoints (orders, balances) can be used.

        Example::

            >>> client = RevolutXClient()
            >>> client.is_authenticated
            False
            >>> client = RevolutXClient(api_key="...", private_key_path="...")
            >>> client.is_authenticated
            True
        """
        return bool(self._api_key and self._has_private_key)

    def __repr__(self) -> str:
        auth = "authenticated" if self.is_authenticated else "public-only"
        return f"<RevolutXClient({auth}, base_url='{self._http.base_url}')>"
