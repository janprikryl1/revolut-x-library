---
name: revolut-x-library
description: >-
  Use this skill when the user asks to interact with the Revolut X Crypto
  Exchange API using Python, when they need to fetch market data (tickers,
  order book, candles, trades), place or manage orders, check account
  balances, or work with any part of the revolut-x-python SDK — including
  authentication setup, fee calculation, order payload building, or error handling.
---

# revolut-x-python SDK

Python SDK for the **Revolut X Crypto Exchange** REST API (v1.0).

- **Python ≥ 3.10** required
- **Dependencies**: `requests>=2.31.0`, `cryptography>=41.0.0`
- **Source**: [src/revolut_x/](./../../src/revolut_x/)
- **Online Documentation (GitHub Pages)**: [https://janprikryl1.github.io/revolut-x-python/](https://janprikryl1.github.io/revolut-x-python/)
- **Repository**: [https://github.com/janprikryl1/revolut-x-python](https://github.com/janprikryl1/revolut-x-python)
- **Sister SDK (PHP)**: [https://github.com/janprikryl1/revolut-x-php](https://github.com/janprikryl1/revolut-x-php)
- **All numeric values from the API are strings** — use `Decimal` for precision

## Installation & Download

### 1. From PyPI / TestPyPI
```bash
# Standard PyPI release:
pip install revolut-x-python

# Or from TestPyPI:
pip install -i https://test.pypi.org/simple/ revolut-x-python
```

### 2. Direct Install from GitHub
```bash
pip install "git+https://github.com/janprikryl1/revolut-x-python.git"
```

### 3. Clone Repository & Install from Source
```bash
git clone https://github.com/janprikryl1/revolut-x-python.git
cd revolut-x-python
pip install .
```

---

## RevolutXClient — Single Entry Point

Composes `MarketMixin` (public) + `OrdersMixin` (auth) + `AccountMixin` (auth).

```python
from revolut_x import RevolutXClient, OrderSide, Interval

# Public data only (no credentials needed)
client = RevolutXClient()

# Authenticated (orders + account)
client = RevolutXClient(
    api_key="pk_live_...",
    private_key_path="keys/private.pem",
)
```

### Constructor (all keyword-only)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str \| None` | `None` | API key (required for auth endpoints) |
| `private_key_path` | `str \| Path \| None` | `None` | Path to Ed25519 PEM private key |
| `private_key_bytes` | `bytes \| None` | `None` | Raw PEM bytes (alternative to path) |
| `base_url` | `str` | `"https://revx.revolut.com/api"` | API base URL |
| `api_version` | `str` | `"1.0"` | API version |
| `request_delay` | `float` | `0.85` | Min seconds between requests |
| `timeout` | `int` | `15` | HTTP timeout (seconds) |
| `max_retries` | `int` | `3` | Retries on 429 / network errors |
| `timestamp_offset_ms` | `int` | `0` | Manual clock offset (ms) for request signing |

`client.is_authenticated → bool` — `True` if both API key and signing key are configured.

### Clock Synchronization

Signed requests carry `X-Revx-Timestamp`; a local clock that drifts more than a
few seconds makes the exchange reject them. The client handles this itself —
before the first authenticated request it reads the server `Date` header and
stores an offset, and it re-syncs automatically on an HTTP 409 timestamp error.
Only touch these if you need to override that:

```python
client.sync_time()              # force a re-sync, returns the new offset in ms
client.timestamp_offset         # → int (ms); alias: client.timestamp_offset_ms
client.timestamp_offset = -500  # manual override
```

---

## Authentication Setup

```bash
# 1. Generate Ed25519 key pair
openssl genpkey -algorithm ed25519 -out private.pem
openssl pkey -in private.pem -pubout -out public.pem

# 2. Upload public.pem to Revolut X → Settings → API
# 3. Pass api_key + private_key_path to the client
```

Headers auto-set: `X-Revx-API-Key`, `X-Revx-Timestamp`, `X-Revx-Signature`.

---

## Market Data (No Auth Required)

```python
client = RevolutXClient()

# Pairs & currencies
pairs = client.get_pairs()                # → dict[str, PairConfig]  (keyed by "BTC/EUR")
pair = client.get_pair("BTC-EUR")         # → PairConfig  (accepts any format)
currencies = client.get_currencies()      # → dict[str, CurrencyConfig]

# Tickers
tickers = client.get_tickers()            # → list[Ticker]
ticker = client.get_ticker("BTC-EUR")     # → Ticker
# ticker["last_price"], ticker["bid"], ticker["ask"], ticker["volume_24h"]
# NOTE: 24h fields are suffixed: volume_24h / high_24h / low_24h
#       (there are no plain "volume" / "high" / "low" keys)

# Order book — always 5 levels per side; the depth argument is ignored
book = client.get_order_book("BTC-EUR")            # → OrderBook
# Levels are DICTS, not [price, qty] pairs:
# book["bids"][0] → {"p": "95000.00", "q": "0.5", "s": "BUYI", "pc": "EUR", ...}
# price = book["bids"][0]["p"]   quantity = book["bids"][0]["q"]

# Candles (OHLCV) — see the dedicated section below
candles = client.get_candles("BTC-EUR", Interval.HOUR_1)

# Public trades — single page + cursor.
# start_date / end_date are Unix MILLISECONDS (int), never date strings —
# a string like "2024-01-01" raises ValueError.
import time
day_ago = int(time.time() * 1000) - 86_400_000
trades, next_cursor = client.get_trades("BTC-EUR", start_date=day_ago, limit=100)

# Auto-paginating trade iterator
for trade in client.iter_trades("BTC-EUR", start_date=day_ago):
    print(trade["price"], trade["side"])
```

---

## Candles (OHLCV)

```python
candles = client.get_candles("BTC-EUR", Interval.HOUR_1)
candles = client.get_candles("BTC-EUR", Interval.DAY_1, since=ts_ms, until=ts_ms)

# Auto-paginating iterator — use for any window wider than 1000 candles
for c in client.iter_candles("BTC-EUR", Interval.MIN_15, since=start, until=end):
    print(c["close"])
```

Each candle is a dict — **not** a list or tuple:

```python
{"start": 1788058800000, "open": "67419.13", "high": "67547.81",
 "low": "67356.94", "close": "67469.02", "volume": "0.09977242"}
```

- `start` — candle **open** time, `int` Unix **milliseconds**, always **UTC**
- `open` / `high` / `low` / `close` / `volume` — **strings**; `volume` is in the
  base currency. Wrap in `Decimal`, never `float`.
- `since` / `until` are also Unix **milliseconds** (`int`), inclusive on both ends.

Three things that make naive candle code wrong:

1. **No `since` ≠ "today".** A bare `get_candles(sym, interval)` returns the most
   recent **1000 candles** (for `HOUR_1` that is ~41 days, not today). Always pass
   an explicit `since` when the user asks for a specific period.
2. **The last candle is still forming.** Its `high`/`low`/`close`/`volume` keep
   changing until the interval ends, so two runs minutes apart legitimately
   return different values for it. Label it or drop it — never present it as a
   closed candle.
3. **A single call spans at most 1000 candles.** A wider `since`/`until` window is
   rejected with HTTP 400 (`Lookup window interval exceeds the limit of 1000
   candles`) — it is *not* silently truncated. Use `iter_candles` instead.

### Reproducible recipe: candles for a calendar day

Use this shape whenever the user asks for "today" / "yesterday" / a given date.
It pins the day to UTC, converts `start` to a readable timestamp, and keeps the
unfinished candle visibly separate — so the same request gives the same answer
regardless of who runs it.

```python
import time
from datetime import datetime, timezone, time as dtime
from decimal import Decimal
from revolut_x import RevolutXClient, Interval

client = RevolutXClient()
interval = Interval.HOUR_1

# The exchange timestamps everything in UTC — define the day in UTC too,
# otherwise the row set shifts with the machine's local timezone.
day = datetime.now(timezone.utc).date()                      # or date(2026, 10, 10)
midnight = datetime.combine(day, dtime.min, tzinfo=timezone.utc)
since = int(midnight.timestamp() * 1000)
until = min(since + 86_400_000 - 1, int(time.time() * 1000))

candles = client.get_candles("BTC-EUR", interval, since=since, until=until)

interval_ms = int(interval) * 60_000
now_ms = int(time.time() * 1000)
closed = [c for c in candles if c["start"] + interval_ms <= now_ms]
forming = [c for c in candles if c["start"] + interval_ms > now_ms]

for c in closed:
    opened = datetime.fromtimestamp(c["start"] / 1000, tz=timezone.utc)
    print(f"{opened:%Y-%m-%d %H:%M} UTC  O={c['open']:>12} H={c['high']:>12} "
          f"L={c['low']:>12} C={c['close']:>12} V={c['volume']:>14}")

# Daily aggregate over CLOSED candles only — reproducible
if closed:
    print("open  ", closed[0]["open"])
    print("high  ", max(Decimal(c["high"]) for c in closed))
    print("low   ", min(Decimal(c["low"]) for c in closed))
    print("close ", closed[-1]["close"])
    print("volume", sum(Decimal(c["volume"]) for c in closed))

for c in forming:
    opened = datetime.fromtimestamp(c["start"] / 1000, tz=timezone.utc)
    print(f"{opened:%H:%M} UTC — in progress, not final: C={c['close']}")
```

Output conventions to follow unless the user asks otherwise: print a table to
stdout (don't export a file), timestamps as `YYYY-MM-DD HH:MM` **UTC** (never raw
epoch numbers), prices and volume verbatim as returned by the API — formatting a
`str` price through `float` loses precision.

---

## Orders (Auth Required)

### Placing Orders

```python
from revolut_x import OrderSide

# Market buy — by quote amount (buy 100 EUR worth of BTC)
order = client.place_market_order("BTC-EUR", OrderSide.BUY, quote_size="100")

# Market sell — by base amount (sell 0.5 BTC)
order = client.place_market_order("BTC-EUR", OrderSide.SELL, base_size="0.5")

# Limit order
order = client.place_limit_order(
    "BTC-EUR", OrderSide.SELL, price="95000",
    base_size="0.001", time_in_force="gtc",
)

# Zero-fee maker order (limit + post_only, auto-calculates price if None)
order = client.place_maker_order("BTC-EUR", OrderSide.BUY, quote_size="50")

# Maker order with explicit price
order = client.place_maker_order("BTC-EUR", OrderSide.BUY, price="94000", base_size="0.001")

# Calculate optimal maker price without placing order
price = client.calculate_maker_price("BTC-EUR", OrderSide.BUY, offset="0.10", tick_size="0.01")

# Generic place_order accepts either individual args or a pre-built payload.
# Only symbol and side are positional — everything else is KEYWORD-ONLY.
order = client.place_order("BTC-EUR", OrderSide.BUY, order_type=OrderType.MARKET, quote_size="100")
order = client.place_order("BTC-EUR", OrderSide.BUY, order_type="limit", price="94000", quote_size="50")
# or:
payload = build_market_order("BTC-EUR", OrderSide.BUY, quote_size="100")
order = client.place_order(payload)
```

### Order Response

```python
order["venue_order_id"]     # exchange-assigned ID
order["client_order_id"]    # your UUID
order["state"]              # e.g. "new"
```

### Querying Orders

```python
detail = client.get_order("order-id")                      # → OrderDetail
fills = client.get_order_fills("order-id")                  # → list[Fill]
active = client.get_active_orders()                         # → list[OrderDetail]
active = client.get_active_orders(symbol="BTC-EUR")         # filtered
history, cursor = client.get_historical_orders(limit=50)    # paginated
```

### Cancelling

```python
client.cancel_order("order-id")
client.cancel_all_orders()                    # all pairs
client.cancel_all_orders(symbol="BTC-EUR")    # specific pair
```

---

## Account (Auth Required)

```python
balances = client.get_balances()                          # → list[Balance]
btc = client.get_balance("BTC")                           # → Balance
txns, cursor = client.get_transactions(limit=50)          # → (list[dict], cursor)
trades, cursor = client.get_account_trades(symbol="BTC-EUR", limit=100)
```

---

## Order Payload Builders (Pure Functions)

Build payloads without making API calls. Useful for validation before submission.

> **Important**: The payload format uses nested `order_configuration` with `"market"` or `"limit"` key.

```python
from revolut_x import (
    OrderPayloadBuilder, build_market_order,
    build_limit_order, build_maker_order, build_order,
)

# Market order payload
payload = build_market_order("BTC-EUR", OrderSide.BUY, quote_size="100")
# → {"client_order_id": "...", "symbol": "BTC-EUR", "side": "buy",
#    "order_configuration": {"market": {"quote_size": "100"}}}

# Limit order payload
payload = build_limit_order("BTC-EUR", OrderSide.SELL, "95000", base_size="0.001")

# Maker order payload (limit + post_only for 0% fee)
payload = build_maker_order("BTC-EUR", OrderSide.BUY, "94000", quote_size="50")

# Generic builder
payload = build_order("BTC-EUR", "buy", "limit", price="95000", base_size="0.001")

# Validate against exchange pair rules BEFORE sending
pair_rules = client.get_pair("BTC-EUR")
is_valid, errors = OrderPayloadBuilder.validate_against_pair_rules(payload, pair_rules)
# is_valid: bool, errors: list[str]
```

---

## Fee Calculator

Maker fee: **0.00%**, Taker fee: **0.09%**

```python
from revolut_x import FeeCalculator, OrderSide

est = FeeCalculator.calculate(
    OrderSide.BUY, price="95000", is_maker=False, quote_size="1000"
)
print(est.fee_amount)          # Decimal, e.g. 0.9000
print(est.fee_rate_percent)    # Decimal, e.g. 0.09
print(est.net_received)        # Decimal — what you actually get
print(est.explanation)         # human-readable multi-line summary
```

### `FeeEstimate` fields

`side`, `order_type`, `is_maker`, `fee_rate_percent`, `trade_value_eur`, `estimated_base_qty`, `price`, `fee_amount`, `fee_currency`, `net_received`, `net_received_currency`, `explanation`

---

## Symbol Normalization

```python
from revolut_x import normalize_symbol

normalize_symbol("btceur")    # → "BTC-EUR"
normalize_symbol("BTC/EUR")   # → "BTC-EUR"
normalize_symbol("btc-eur")   # → "BTC-EUR"
```

Supported quote currencies for auto-detection: `EUR`, `USD`, `USDC`, `GBP`, `CZK`.

---

## Maker Price Calculation

```python
from revolut_x import calculate_maker_price, OrderSide

# BUY: price = best_bid - offset → enters order book below best bid
price = calculate_maker_price(
    OrderSide.BUY, best_bid="80000.00", offset="0.10"
)  # → Decimal("79999.90")

# SELL: price = best_ask + offset → enters order book above best ask
price = calculate_maker_price(
    OrderSide.SELL, best_ask="80000.50", offset="0.10"
)  # → Decimal("80000.60")
```

---

## Error Handling

```python
from revolut_x import (
    RevolutXError, AuthenticationError, RateLimitError,
    ApiError, OrderValidationError, NetworkError,
)

try:
    client.place_market_order(...)
except AuthenticationError as e:
    print(e.hint)                  # human-readable suggestion
except RateLimitError as e:
    print(e.retry_after_seconds)   # Retry-After header value
    print(e.endpoint)
except OrderValidationError as e:
    print(e.errors)                # list[str] of validation messages
except ApiError as e:
    print(e.status_code, e.response_body, e.endpoint, e.method)
except NetworkError as e:
    print(e.original_error)        # underlying requests exception
```

Exception hierarchy:
```
RevolutXError (base)
├── AuthenticationError     → 401/403 or missing credentials (.hint)
├── RateLimitError          → 429 after retries (.retry_after_seconds, .endpoint)
├── ApiError                → other HTTP errors (.status_code, .response_body)
├── OrderValidationError    → client-side validation (.errors: list[str])
│                             also inherits ValueError
└── NetworkError            → connection/timeout (.original_error)
```

---

## Enums

```python
from revolut_x import OrderSide, OrderType, Interval, TimeInForce

OrderSide.BUY / OrderSide.SELL
OrderType.MARKET / OrderType.LIMIT
TimeInForce.GTC / TimeInForce.IOC

# Interval — candlestick resolution in minutes
Interval.MIN_1   # 1      Interval.HOUR_1  # 60     Interval.DAY_1  # 1440
Interval.MIN_5   # 5      Interval.HOUR_4  # 240    Interval.DAY_2  # 2880
Interval.MIN_15  # 15                                Interval.DAY_4  # 5760
Interval.MIN_30  # 30     Interval.WEEK_1  # 10080  Interval.WEEK_2 # 20160
                           Interval.WEEK_4  # 40320
```

---

## Key Design Notes

- **Mixin architecture**: `RevolutXClient(MarketMixin, OrdersMixin, AccountMixin)` — all share `self._http`
- **Rate limiting**: built-in 0.85s delay + exponential backoff on 429
- **All API numeric values are strings** — use `Decimal` for precision, never `float`
- **Symbol format**: API uses `BASE/QUOTE` (e.g. `"BTC/EUR"`) but `normalize_symbol()` accepts `BTC-EUR`, `btceur`, etc.
- **Pagination**: `get_trades`, `get_historical_orders`, `get_transactions`, `get_account_trades` return `(items, next_cursor)` tuples; `iter_candles` / `iter_trades` auto-paginate
- **Order payload format**: nested `order_configuration` with `"market"` or `"limit"` key
- **Fee model**: Maker 0.00%, Taker 0.09%

For full type definitions, see [references/types.md](./references/types.md).

---

## Development & Documentation

```bash
# Development install (tests + dev tools)
pip install -e ".[dev]"
pytest                      # run test suite (43 tests)

# Documentation install & commands
pip install -e ".[docs]"
mkdocs serve                # local live preview at http://127.0.0.1:8000
mkdocs build                # build static HTML to site/
mkdocs gh-deploy            # deploy static docs to GitHub Pages

# Online Docs: https://janprikryl1.github.io/revolut-x-python/
# GitHub Repo: https://github.com/janprikryl1/revolut-x-python
```
