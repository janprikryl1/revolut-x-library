# Types Reference

Complete type definitions for the revolut-x-python SDK. All types are defined in
[`types.py`](./../../../src/revolut_x/types.py).
Online interactive documentation: [https://janprikryl1.github.io/revolut-x-library/api/types/](https://janprikryl1.github.io/revolut-x-library/api/types/)

## Enums

All enums are `str` (or `int`) subclasses — they can be used directly as string/int values.

```python
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class TimeInForce(str, Enum):
    GTC = "gtc"   # Good-Til-Cancelled
    IOC = "ioc"   # Immediate-Or-Cancel

class Interval(int, Enum):
    MIN_1 = 1       # 1-minute candles
    MIN_5 = 5
    MIN_15 = 15
    MIN_30 = 30
    HOUR_1 = 60
    HOUR_4 = 240
    DAY_1 = 1440
    DAY_2 = 2880
    DAY_4 = 5760
    WEEK_1 = 10080
    WEEK_2 = 20160
    WEEK_4 = 40320
```

## TypedDicts (API Responses)

> All numeric values are **strings** (not floats) to preserve decimal precision.
> Timestamps are `int` (Unix milliseconds).

### Candle

```python
class Candle(TypedDict):
    start: int       # Unix timestamp (ms), candle open time
    open: str
    high: str
    low: str
    close: str
    volume: str      # Base currency volume
```

### Trade

```python
class Trade(TypedDict, total=False):
    id: str           # UUID
    symbol: str       # e.g. "BTC/EUR"
    price: str
    quantity: str     # Base currency
    timestamp: int    # Unix ms
    side: str         # "buy" | "sell"
    region: str       # e.g. "EEA", "UK"
```

### Ticker

```python
class Ticker(TypedDict, total=False):
    symbol: str             # e.g. "BTC/EUR"
    bid: str                # Best bid (highest buy)
    ask: str                # Best ask (lowest sell)
    mid: str                # Midpoint of bid/ask
    index_price: str        # Reference index price
    last_price: str
    high_24h: str           # 24h high
    low_24h: str            # 24h low
    price_change_24h: str   # Absolute 24h change
    volume_24h: str         # 24h volume in base currency
    quote_volume_24h: str   # 24h volume in quote currency
    region: str             # e.g. "EEA", "UK"
```

The 24-hour fields carry the `_24h` suffix; plain `high` / `low` / `volume`
keys do **not** exist in the response.

### PairConfig

```python
class PairConfig(TypedDict, total=False):
    base: str                  # e.g. "BTC"
    quote: str                 # e.g. "EUR"
    base_step: str             # Min quantity increment, e.g. "0.00000001"
    quote_step: str            # Min price increment, e.g. "0.01"
    min_order_size: str        # Min base qty
    max_order_size: str        # Max base qty
    min_order_size_quote: str  # Min quote amount
    max_order_size_quote: str  # Max quote amount
    status: str                # "active" | "inactive"
    slippage: int              # Max allowed slippage %
```

### CurrencyConfig

```python
class CurrencyConfig(TypedDict, total=False):
    name: str          # e.g. "Bitcoin"
    symbol: str        # e.g. "BTC"
    scale: int         # Decimal places
    asset_type: str    # "crypto" | "fiat"
    status: str        # "active" | "inactive"
```

### OrderBook

```python
class OrderBookLevel(TypedDict, total=False):
    p: str     # Price in quote currency   <- the one you want
    q: str     # Quantity in base currency <- the one you want
    s: str     # "BUYI" (bid) | "SELL" (ask)
    pc: str    # Price currency, e.g. "EUR"
    qc: str    # Quantity currency, e.g. "BTC"
    aid: str   # Asset id, e.g. "BTC"
    anm: str   # Asset name, e.g. "Bitcoin"
    no: str    # Number of orders at this level
    pn: str    # Price notation, e.g. "MONE"
    qn: str    # Quantity notation, e.g. "UNIT"
    ve: str    # Venue, e.g. "REVX"
    ts: str    # Trading system, e.g. "CLOB"
    pdt: str   # Price timestamp (ISO-8601)


class OrderBook(TypedDict):
    bids: list[OrderBookLevel]   # dicts, sorted best (highest) first
    asks: list[OrderBookLevel]   # dicts, sorted best (lowest) first
```

Levels are dictionaries, **not** `[price, qty]` pairs — the exchange always
returns 5 levels per side:

```python
best_bid = book["bids"][0]
best_bid["p"]   # "73875.00"  price
best_bid["q"]   # "0.04966288"  quantity
```

### Balance

```python
class Balance(TypedDict):
    currency: str      # e.g. "EUR", "BTC"
    available: str     # Available for trading
    reserved: str      # Locked in open orders
    total: str         # available + reserved
```

### OrderResponse

```python
class OrderResponse(TypedDict, total=False):
    venue_order_id: str      # Exchange-assigned order ID
    client_order_id: str     # Client-provided UUID
    state: str               # e.g. "new"
```

### OrderDetail

```python
class OrderDetail(TypedDict, total=False):
    id: str
    symbol: str
    side: str                  # "buy" | "sell"
    type: str                  # "market" | "limit"
    status: str                # "new", "filled", "canceled", ...
    quantity: str              # Requested base qty
    filled_quantity: str       # Actually filled base qty
    amount: str                # Requested quote amount
    filled_amount: str         # Actually filled quote amount
    average_fill_price: str    # VWAP
    total_fee: str
    fee_currency: str          # e.g. "EUR"
    created_date: int          # Unix ms
    updated_date: int          # Unix ms
```

### Fill

```python
class Fill(TypedDict, total=False):
    tdt: int       # Trade timestamp (Unix ms)
    aid: str       # Asset ID, e.g. "BTC"
    anm: str       # Asset name, e.g. "Bitcoin"
    p: str         # Execution price
    pc: str        # Price currency, e.g. "EUR"
    q: str         # Filled quantity
    qc: str        # Quantity currency, e.g. "BTC"
    tid: str       # Trade ID
    oid: str       # Order ID
    s: str         # Side ("buy" | "sell")
    im: bool       # True if maker trade (0% fee)
```

## Helper Types

### FeeEstimate

```python
@dataclass
class FeeEstimate:
    side: str                        # "buy" | "sell"
    order_type: str                  # "limit" | "market/immediate-limit"
    is_maker: bool
    fee_rate_percent: Decimal        # e.g. Decimal("0.09")
    trade_value_eur: Decimal         # Total trade value in quote currency
    estimated_base_qty: Decimal      # Estimated base quantity
    price: Decimal
    fee_amount: Decimal              # Fee in fee_currency
    fee_currency: str                # "EUR"
    net_received: Decimal            # What you actually receive
    net_received_currency: str       # "BTC" (buy) or "EUR" (sell)
    explanation: str                 # Multi-line human-readable summary
```

## Exception Hierarchy

```python
class RevolutXError(Exception):
    """Base — catch-all for any SDK error."""

class AuthenticationError(RevolutXError):
    hint: str | None                       # Human-readable fix suggestion

class RateLimitError(RevolutXError):
    retry_after_seconds: float | None      # Retry-After header
    endpoint: str | None

class ApiError(RevolutXError):
    status_code: int
    response_body: Any
    endpoint: str
    method: str

class OrderValidationError(RevolutXError, ValueError):
    errors: list[str]                      # Individual validation messages

class NetworkError(RevolutXError):
    original_error: Exception | None       # Underlying requests exception
```

## Order Payload Format

The SDK uses a nested `order_configuration` structure:

```python
# Market order payload
{
    "client_order_id": "uuid-string",
    "symbol": "BTC-EUR",
    "side": "buy",
    "order_configuration": {
        "market": {
            "quote_size": "100"          # or "base_size": "0.5"
        }
    }
}

# Limit order payload
{
    "client_order_id": "uuid-string",
    "symbol": "BTC-EUR",
    "side": "sell",
    "order_configuration": {
        "limit": {
            "price": "95000",
            "base_size": "0.001",        # or "quote_size"
            "time_in_force": "gtc",
            "execution_instructions": ["allow_taker"]   # or ["post_only"]
        }
    }
}
```
