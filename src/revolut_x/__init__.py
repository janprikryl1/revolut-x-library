"""revolut-x-python — Python SDK for the Revolut X Crypto Exchange REST API.

Quick start::

    from revolut_x import RevolutXClient, OrderSide, Interval

    # Public market data (no API key required)
    client = RevolutXClient()
    ticker = client.get_ticker("BTC-EUR")
    candles = client.get_candles("BTC-EUR", Interval.HOUR_1)

    # Trading (requires API key + Ed25519 private key)
    client = RevolutXClient(
        api_key="your-api-key",
        private_key_path="keys/private.pem",
    )
    order = client.place_market_order("BTC-EUR", OrderSide.BUY, quote_size="50.00")
    balances = client.get_balances()

For full documentation, see https://github.com/janprikryl/revolut-x-python
"""

from __future__ import annotations
from revolut_x._version import __version__
from revolut_x.client import RevolutXClient
from revolut_x.types import (
    OrderSide,
    OrderType,
    Interval,
    TimeInForce,
    # TypedDicts
    Balance,
    Candle,
    CurrencyConfig,
    Fill,
    OrderBook,
    OrderBookLevel,
    OrderDetail,
    OrderResponse,
    PairConfig,
    Ticker,
    Trade,
)
from revolut_x.helpers import (
    FeeCalculator,
    FeeEstimate,
    OrderPayloadBuilder,
    build_limit_order,
    build_maker_order,
    build_market_order,
    build_order,
    calculate_maker_price,
    normalize_symbol,
)
from revolut_x.exceptions import (
    ApiError,
    AuthenticationError,
    NetworkError,
    OrderValidationError,
    RateLimitError,
    RevolutXError,
)

__all__ = [
    # Metadata
    "__version__",
    # Client
    "RevolutXClient",
    # Enums
    "OrderSide",
    "OrderType",
    "Interval",
    "TimeInForce",
    # Helpers
    "OrderPayloadBuilder",
    "FeeCalculator",
    "FeeEstimate",
    "normalize_symbol",
    "calculate_maker_price",
    "build_order",
    "build_market_order",
    "build_limit_order",
    "build_maker_order",
    # Type definitions
    "Balance",
    "Candle",
    "CurrencyConfig",
    "Fill",
    "OrderBook",
    "OrderBookLevel",
    "OrderDetail",
    "OrderResponse",
    "PairConfig",
    "Ticker",
    "Trade",
    # Exceptions
    "RevolutXError",
    "AuthenticationError",
    "RateLimitError",
    "ApiError",
    "OrderValidationError",
    "NetworkError",
]
