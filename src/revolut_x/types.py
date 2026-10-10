"""Type definitions, enums, and typed dictionaries for revolut-x-python.

This module provides:

* **Enums** — :class:`OrderSide`, :class:`OrderType`, :class:`Interval`,
  :class:`TimeInForce` for type-safe parameter passing.
* **TypedDicts** — :class:`Candle`, :class:`Trade`, :class:`Ticker`,
  :class:`Balance`, :class:`PairConfig`, etc. for IDE autocompletion
  on API response data.
"""

from __future__ import annotations
from enum import Enum
from typing import TypedDict


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OrderSide(str, Enum):
    """Direction of an order.

    Example::

        from revolut_x import OrderSide
        side = OrderSide.BUY
    """

    BUY = "buy"
    """Buy the base currency (e.g. buy BTC for EUR)."""

    SELL = "sell"
    """Sell the base currency (e.g. sell BTC for EUR)."""


class OrderType(str, Enum):
    """Type of an order.

    Example::

        from revolut_x import OrderType
        order_type = OrderType.LIMIT
    """

    MARKET = "market"
    """Market order — executed immediately at the best available price (taker fee: 0.09%)."""

    LIMIT = "limit"
    """Limit order — placed in the order book at a specific price (maker fee: 0.00%)."""


class Interval(int, Enum):
    """Candlestick interval in minutes, as accepted by the Revolut X API.

    Example::

        from revolut_x import Interval
        candles = client.get_candles("BTC-EUR", interval=Interval.HOUR_1)
    """

    MIN_1 = 1
    """1-minute candles."""

    MIN_5 = 5
    """5-minute candles."""

    MIN_15 = 15
    """15-minute candles."""

    MIN_30 = 30
    """30-minute candles."""

    HOUR_1 = 60
    """1-hour candles."""

    HOUR_4 = 240
    """4-hour candles."""

    DAY_1 = 1440
    """1-day (24h) candles."""

    DAY_2 = 2880
    """2-day candles."""

    DAY_4 = 5760
    """4-day candles."""

    WEEK_1 = 10080
    """1-week candles."""

    WEEK_2 = 20160
    """2-week candles."""

    WEEK_4 = 40320
    """4-week (28-day) candles."""


class TimeInForce(str, Enum):
    """Time-in-force policy for limit orders.

    Example::

        from revolut_x import TimeInForce
        client.place_limit_order(..., time_in_force=TimeInForce.GTC)
    """

    GTC = "gtc"
    """Good 'til canceled — the order stays open until filled or manually canceled."""

    IOC = "ioc"
    """Immediate or cancel — fill as much as possible immediately, cancel the rest."""


# ---------------------------------------------------------------------------
# TypedDicts — structured response types for IDE autocompletion
# ---------------------------------------------------------------------------

class Candle(TypedDict):
    """A single OHLCV candlestick returned by :meth:`RevolutXClient.get_candles`.

    Attributes:
        start: Candle open time as Unix timestamp in milliseconds.
        open: Opening price (string to preserve decimal precision).
        high: Highest price during the interval.
        low: Lowest price during the interval.
        close: Closing price.
        volume: Trading volume in the base currency.
    """

    start: int
    open: str
    high: str
    low: str
    close: str
    volume: str


class Trade(TypedDict, total=False):
    """A single public trade returned by :meth:`RevolutXClient.get_trades`.

    Attributes:
        id: Unique trade identifier (UUID string).
        symbol: Trading pair (e.g. ``'BTC/EUR'``).
        price: Execution price.
        quantity: Traded quantity in the base currency.
        timestamp: Trade time as Unix timestamp in milliseconds.
        side: ``'buy'`` or ``'sell'``.
        region: Venue region the trade was executed in (e.g. ``'EEA'``, ``'UK'``).
    """

    id: str
    symbol: str
    price: str
    quantity: str
    timestamp: int
    side: str
    region: str


class Ticker(TypedDict, total=False):
    """Ticker data for a trading pair from :meth:`RevolutXClient.get_ticker`.

    Attributes:
        symbol: Trading pair (e.g. ``'BTC/EUR'``).
        bid: Best bid (highest buy) price.
        ask: Best ask (lowest sell) price.
        mid: Midpoint between ``bid`` and ``ask``.
        index_price: Reference index price.
        last_price: Last traded price.
        low_24h: 24-hour low price.
        high_24h: 24-hour high price.
        price_change_24h: Absolute price change over the last 24 hours.
        volume_24h: 24-hour trading volume in the base currency.
        quote_volume_24h: 24-hour trading volume in the quote currency.
        region: Venue region (e.g. ``'EEA'``, ``'UK'``).
    """

    symbol: str
    bid: str
    ask: str
    mid: str
    index_price: str
    last_price: str
    low_24h: str
    high_24h: str
    price_change_24h: str
    volume_24h: str
    quote_volume_24h: str
    region: str


class PairConfig(TypedDict, total=False):
    """Configuration and trading limits for a single pair.

    Returned by :meth:`RevolutXClient.get_pairs` and
    :meth:`RevolutXClient.get_pair`.

    Attributes:
        base: Base currency symbol (e.g. ``'BTC'``).
        quote: Quote currency symbol (e.g. ``'EUR'``).
        base_step: Minimum quantity increment (e.g. ``'0.00000001'``).
        quote_step: Minimum price increment (e.g. ``'0.01'``).
        min_order_size: Minimum order size in the base currency.
        max_order_size: Maximum order size in the base currency.
        min_order_size_quote: Minimum order value in the quote currency.
        max_order_size_quote: Maximum order value in the quote currency.
        status: Pair status — ``'active'`` or ``'inactive'``.
        slippage: Maximum allowed slippage percentage.
    """

    base: str
    quote: str
    base_step: str
    quote_step: str
    min_order_size: str
    max_order_size: str
    min_order_size_quote: str
    max_order_size_quote: str
    status: str
    slippage: int


class CurrencyConfig(TypedDict, total=False):
    """Configuration for a single currency.

    Returned by :meth:`RevolutXClient.get_currencies`.

    Attributes:
        name: Human-readable currency name (e.g. ``'Bitcoin'``).
        symbol: Currency ticker (e.g. ``'BTC'``).
        scale: Number of decimal places.
        asset_type: ``'crypto'`` or ``'fiat'``.
        status: ``'active'`` or ``'inactive'``.
    """

    name: str
    symbol: str
    scale: int
    asset_type: str
    status: str


class OrderBookLevel(TypedDict, total=False):
    """A single price level in the order book.

    The Revolut X order book uses short field names.  The two fields you
    normally want are ``p`` (price) and ``q`` (quantity).

    Attributes:
        p: Price in the quote currency.
        q: Quantity available at this price, in the base currency.
        s: Side — ``'BUYI'`` for bids, ``'SELL'`` for asks.
        pc: Price currency (e.g. ``'EUR'``).
        qc: Quantity currency (e.g. ``'BTC'``).
        aid: Asset identifier (e.g. ``'BTC'``).
        anm: Asset name (e.g. ``'Bitcoin'``).
        no: Number of orders aggregated into this level.
        pn: Price notation (e.g. ``'MONE'``).
        qn: Quantity notation (e.g. ``'UNIT'``).
        ve: Venue (e.g. ``'REVX'``).
        ts: Trading system (e.g. ``'CLOB'``).
        pdt: Price timestamp as an ISO-8601 string.
    """

    p: str
    q: str
    s: str
    pc: str
    qc: str
    aid: str
    anm: str
    no: str
    pn: str
    qn: str
    ve: str
    ts: str
    pdt: str


class OrderBook(TypedDict):
    """Order book snapshot from :meth:`RevolutXClient.get_order_book`.

    Each entry is an :class:`OrderBookLevel` dictionary — **not** a
    ``[price, quantity]`` pair.  Read the price and quantity from the
    ``p`` and ``q`` keys::

        best_bid = book["bids"][0]
        print(best_bid["p"], best_bid["q"])

    Attributes:
        bids: Buy levels, sorted best (highest price) first.
        asks: Sell levels, sorted best (lowest price) first.
    """

    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]


class Balance(TypedDict):
    """Account balance for a single currency.

    Returned by :meth:`RevolutXClient.get_balances`.

    Attributes:
        currency: Currency symbol (e.g. ``'EUR'``, ``'BTC'``).
        available: Amount available for trading.
        reserved: Amount locked in open orders.
        total: Total balance (available + reserved).
    """

    currency: str
    available: str
    reserved: str
    total: str


class OrderResponse(TypedDict, total=False):
    """Response returned after placing a new order.

    Attributes:
        venue_order_id: Exchange-assigned order ID.
        client_order_id: Client-provided order ID (UUID).
        state: Initial order state (e.g. ``'new'``).
    """

    venue_order_id: str
    client_order_id: str
    state: str


class OrderDetail(TypedDict, total=False):
    """Detailed order information from :meth:`RevolutXClient.get_order`.

    Attributes:
        id: Exchange order ID.
        symbol: Trading pair.
        side: ``'buy'`` or ``'sell'``.
        type: ``'market'`` or ``'limit'``.
        status: Order status (``'new'``, ``'filled'``, ``'canceled'``, …).
        quantity: Requested quantity.
        filled_quantity: Actually filled quantity.
        amount: Requested amount in quote currency.
        filled_amount: Actually filled amount in quote currency.
        average_fill_price: Volume-weighted average fill price.
        total_fee: Total fee charged.
        fee_currency: Currency of the fee (e.g. ``'EUR'``).
        created_date: Creation timestamp in milliseconds.
        updated_date: Last update timestamp in milliseconds.
    """

    id: str
    symbol: str
    side: str
    type: str
    status: str
    quantity: str
    filled_quantity: str
    amount: str
    filled_amount: str
    average_fill_price: str
    total_fee: str
    fee_currency: str
    created_date: int
    updated_date: int


class Fill(TypedDict, total=False):
    """A single fill (partial execution) of an order.

    Returned by :meth:`RevolutXClient.get_order_fills`.

    Attributes:
        tdt: Trade timestamp in milliseconds.
        aid: Asset ID (e.g. ``'BTC'``).
        anm: Asset name (e.g. ``'Bitcoin'``).
        p: Execution price.
        pc: Price currency (e.g. ``'EUR'``).
        q: Filled quantity.
        qc: Quantity currency (e.g. ``'BTC'``).
        tid: Trade ID.
        oid: Order ID.
        s: Side (``'buy'`` or ``'sell'``).
        im: ``True`` if this fill was a maker trade (0% fee).
    """

    tdt: int
    aid: str
    anm: str
    p: str
    pc: str
    q: str
    qc: str
    tid: str
    oid: str
    s: str
    im: bool
