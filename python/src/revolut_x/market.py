"""Public market data methods for the Revolut X API.

This module provides :class:`MarketMixin`, which is mixed into
:class:`~revolut_x.client.RevolutXClient` to add public (unauthenticated)
endpoints for market data: trading pairs, currencies, tickers, order book,
candlestick charts (OHLCV), and public trade history.

All methods in this mixin work **without** an API key.
"""

from __future__ import annotations
import logging
from typing import Any, Iterator, TYPE_CHECKING
from revolut_x.types import (
    Candle,
    CurrencyConfig,
    Interval,
    OrderBook,
    PairConfig,
    Ticker,
    Trade,
)
from revolut_x.helpers import normalize_symbol as _normalize_symbol

if TYPE_CHECKING:
    from revolut_x._http import HttpClient

logger = logging.getLogger(__name__)


class MarketMixin:
    """Public market data endpoints — no authentication required.

    This mixin is not meant to be used directly.  It is mixed into
    :class:`~revolut_x.client.RevolutXClient`.
    """

    # Provided by RevolutXClient
    _http: HttpClient

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def get_pairs(self) -> dict[str, PairConfig]:
        """Retrieve the configuration and trading limits for all active pairs.

        Returns:
            A dictionary mapping pair symbols (e.g. ``'BTC/EUR'``) to their
            :class:`~revolut_x.types.PairConfig` configuration, including
            minimum/maximum order sizes, price/quantity step sizes, and status.

        Raises:
            ApiError: If the API returns a non-2xx response.
            NetworkError: On connection failure.

        Example::

            >>> client = RevolutXClient()
            >>> pairs = client.get_pairs()
            >>> btc = pairs["BTC/EUR"]
            >>> print(f"Min order: {btc['min_order_size']} BTC")
            Min order: 0.00000001 BTC
        """
        _status, data = self._http.request("GET", "/public/configuration/pairs")
        return data

    def get_pair(self, symbol: str) -> PairConfig:
        """Retrieve the configuration for a specific trading pair.

        Args:
            symbol: Trading pair in any common format
                (e.g. ``'BTC-EUR'``, ``'BTC/EUR'``, ``'btceur'``).

        Returns:
            The :class:`~revolut_x.types.PairConfig` for the requested pair.

        Raises:
            ValueError: If the pair is not found or not active on the exchange.
            ApiError: If the API returns a non-2xx response.

        Example::

            >>> pair = client.get_pair("ETH-EUR")
            >>> print(f"Step: {pair['base_step']}")
        """
        pairs = self.get_pairs()

        # Try both slash and dash formats (API returns slash-keyed dict)
        clean_slash = symbol.replace("-", "/").upper()
        clean_dash = symbol.replace("/", "-").upper()

        info = pairs.get(clean_slash) or pairs.get(clean_dash)
        if info is not None:
            return info

        # Case-insensitive fallback
        for key, val in pairs.items():
            if key.upper() in (clean_slash, clean_dash):
                return val

        available = ", ".join(sorted(pairs.keys())[:10])
        raise ValueError(
            f"Trading pair '{symbol}' not found on Revolut X. "
            f"Available pairs include: {available}… "
            f"Use get_pairs() to see the full list."
        )

    def get_currencies(self) -> dict[str, CurrencyConfig]:
        """Retrieve the configuration for all supported currencies.

        Returns:
            A dictionary mapping currency symbols (e.g. ``'BTC'``, ``'EUR'``)
            to their :class:`~revolut_x.types.CurrencyConfig`.

        Raises:
            ApiError: If the API returns a non-2xx response.

        Example::

            >>> currencies = client.get_currencies()
            >>> print(currencies["BTC"]["name"])
            Bitcoin
        """
        _status, data = self._http.request("GET", "/public/configuration/currencies")
        return data

    # ------------------------------------------------------------------
    # Tickers & Order Book
    # ------------------------------------------------------------------

    def get_tickers(self) -> list[Ticker]:
        """Retrieve current tickers (best bid, best ask, last price) for all pairs.

        Returns:
            A list of :class:`~revolut_x.types.Ticker` dictionaries.

        Raises:
            ApiError: If the API returns a non-2xx response.
        """
        _status, data = self._http.request("GET", "/public/tickers")
        if isinstance(data, dict):
            return data.get("data", [])
        return data

    def get_ticker(self, symbol: str) -> Ticker:
        """Retrieve the current ticker for a specific trading pair.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).

        Returns:
            A :class:`~revolut_x.types.Ticker` with best bid, best ask,
            and last traded price.

        Raises:
            ValueError: If ticker data is not available for the given symbol.
            ApiError: If the API returns a non-2xx response.

        Example::

            >>> ticker = client.get_ticker("BTC-EUR")
            >>> print(f"BTC price: {ticker['last_price']} EUR")
        """
        tickers = self.get_tickers()

        target_slash = symbol.replace("-", "/").upper()
        target_dash = symbol.replace("/", "-").upper()

        if isinstance(tickers, list):
            for t in tickers:
                sym = t.get("symbol", "").upper()
                if sym in (target_slash, target_dash):
                    return t
        elif isinstance(tickers, dict):
            result = tickers.get(target_slash) or tickers.get(target_dash)
            if result is not None:
                return result

        raise ValueError(
            f"Ticker data not available for '{symbol}'. "
            f"Check that the pair exists with get_pairs()."
        )

    def get_order_book(self, symbol: str, depth: int = 10) -> OrderBook:
        """Retrieve the current order book (bids and asks) for a trading pair.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            depth: Number of price levels to retrieve (default: 10).

        Returns:
            An :class:`~revolut_x.types.OrderBook` with ``bids`` and ``asks``
            lists, each containing ``[price, quantity]`` pairs sorted
            best-first.

        Raises:
            ApiError: If the API returns a non-2xx response.

        Example::

            >>> book = client.get_order_book("BTC-EUR", depth=5)
            >>> best_bid = book["bids"][0]
            >>> print(f"Best bid: {best_bid[0]} EUR")
        """
        api_symbol = _normalize_symbol(symbol)
        _status, data = self._http.request(
            "GET",
            f"/public/order-book/{api_symbol}",
            params={"limit": depth},
        )
        if isinstance(data, dict):
            return data.get("data", data)
        return data

    # ------------------------------------------------------------------
    # Candles (OHLCV)
    # ------------------------------------------------------------------

    def get_candles(
        self,
        symbol: str,
        interval: Interval | int = Interval.HOUR_1,
        *,
        since: int | None = None,
        until: int | None = None,
    ) -> list[Candle]:
        """Fetch up to 1000 OHLCV candlesticks for a trading pair.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            interval: Candle interval — use the :class:`~revolut_x.types.Interval`
                enum (e.g. ``Interval.MIN_1``, ``Interval.HOUR_1``) or an integer
                number of minutes.
            since: Start time as Unix timestamp in **milliseconds** (inclusive).
            until: End time as Unix timestamp in **milliseconds** (inclusive).

        Returns:
            A list of :class:`~revolut_x.types.Candle` dictionaries with keys:
            ``start``, ``open``, ``high``, ``low``, ``close``, ``volume``.

        Note:
            The API returns at most **1000 candles** per request.  To download
            a longer time range, use :meth:`iter_candles` which automatically
            paginates through the data.

        Raises:
            ApiError: If the API returns a non-2xx response.

        Example::

            >>> from revolut_x import Interval
            >>> candles = client.get_candles("BTC-EUR", Interval.HOUR_1,
            ...                              since=1700000000000)
            >>> for c in candles[:3]:
            ...     print(f"{c['start']}: O={c['open']} H={c['high']}")
        """
        api_symbol = _normalize_symbol(symbol)
        params: dict[str, Any] = {"interval": int(interval)}
        if since is not None:
            params["since"] = int(since)
        if until is not None:
            params["until"] = int(until)

        _status, data = self._http.request(
            "GET",
            f"/public/candles/{api_symbol}",
            params=params,
        )

        if isinstance(data, dict):
            return data.get("data", [])
        return data

    def iter_candles(
        self,
        symbol: str,
        interval: Interval | int = Interval.HOUR_1,
        *,
        since: int | None = None,
        until: int | None = None,
    ) -> Iterator[Candle]:
        """Iterate over all candles in a time range, automatically paginating.

        This is a generator that yields :class:`~revolut_x.types.Candle`
        dictionaries one by one, fetching additional pages from the API as
        needed.  It handles the 1000-candle-per-request limit transparently.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            interval: Candle interval (see :meth:`get_candles`).
            since: Start time as Unix timestamp in **milliseconds**.
            until: End time as Unix timestamp in **milliseconds**.

        Yields:
            :class:`~revolut_x.types.Candle` dictionaries in chronological
            order (oldest first).

        Example::

            >>> for candle in client.iter_candles("BTC-EUR", Interval.MIN_1,
            ...                                   since=1700000000000):
            ...     process(candle)  # each candle is a dict
        """
        interval_ms = int(interval) * 60 * 1000  # interval in milliseconds
        max_batch_ms = 999 * interval_ms  # Revolut X limits window to max 1000 candles
        current_since = since

        while True:
            batch_until = None
            if current_since is not None:
                chunk_until = current_since + max_batch_ms
                if until is not None:
                    batch_until = min(until, chunk_until)
                else:
                    batch_until = chunk_until
            elif until is not None:
                batch_until = until

            batch = self.get_candles(
                symbol, interval, since=current_since, until=batch_until
            )
            if not batch:
                break

            yield from batch

            if len(batch) < 1000 and (batch_until == until or until is None):
                # Last page — fewer than max results
                break

            # Move window forward: start after the last candle
            last_start = batch[-1].get("start", 0)
            current_since = int(last_start) + interval_ms

            if until is not None and current_since > until:
                break

    # ------------------------------------------------------------------
    # Public Trades
    # ------------------------------------------------------------------

    def get_trades(
        self,
        symbol: str,
        *,
        start_date: int | None = None,
        end_date: int | None = None,
        cursor: str | None = None,
        limit: int = 1900,
    ) -> tuple[list[Trade], str | None]:
        """Fetch a single page of public trades (up to 1900 per request).

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            start_date: Start time as Unix timestamp in **milliseconds**.
            end_date: End time as Unix timestamp in **milliseconds**.
            cursor: Pagination cursor from a previous response's
                ``metadata.next_cursor`` field.
            limit: Maximum number of trades to return (1–1900, default: 1900).

        Returns:
            A tuple of ``(trades, next_cursor)`` where ``trades`` is a list of
            :class:`~revolut_x.types.Trade` dicts and ``next_cursor`` is a
            string for fetching the next page (or ``None`` if no more data).

        Raises:
            ApiError: If the API returns a non-2xx response.

        Example::

            >>> trades, cursor = client.get_trades("BTC-EUR", limit=100)
            >>> print(f"Got {len(trades)} trades, next cursor: {cursor}")
        """
        api_symbol = _normalize_symbol(symbol)
        params: dict[str, Any] = {
            "symbol": api_symbol,
            "limit": min(limit, 1900),
        }
        if start_date is not None:
            params["start_date"] = int(start_date)
        if end_date is not None:
            params["end_date"] = int(end_date)
        if cursor:
            params["cursor"] = cursor

        _status, data = self._http.request(
            "GET", "/public/trades/all", params=params
        )

        if isinstance(data, dict):
            trades = data.get("data", [])
            next_cursor = data.get("metadata", {}).get("next_cursor")
        else:
            trades = data if isinstance(data, list) else []
            next_cursor = None

        return trades, next_cursor

    def iter_trades(
        self,
        symbol: str,
        *,
        start_date: int | None = None,
        end_date: int | None = None,
        limit: int = 1900,
    ) -> Iterator[Trade]:
        """Iterate over all public trades in a time range, automatically paginating.

        This generator fetches pages of trades using cursor-based pagination
        and yields :class:`~revolut_x.types.Trade` dicts one by one.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            start_date: Start time as Unix timestamp in **milliseconds**.
            end_date: End time as Unix timestamp in **milliseconds**.
            limit: Page size per request (1–1900, default: 1900).

        Yields:
            :class:`~revolut_x.types.Trade` dictionaries.

        Example::

            >>> for trade in client.iter_trades("BTC-EUR",
            ...                                 start_date=1700000000000):
            ...     print(f"{trade['price']} EUR x {trade['quantity']} BTC")
        """
        cursor: str | None = None

        while True:
            trades, next_cursor = self.get_trades(
                symbol,
                start_date=start_date,
                end_date=end_date,
                cursor=cursor,
                limit=limit,
            )
            if not trades:
                break

            yield from trades

            if not next_cursor:
                break

            cursor = next_cursor
