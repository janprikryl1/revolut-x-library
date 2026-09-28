# revolut-x-python

> Python SDK for the Revolut X Crypto Exchange REST API

[![Python version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust, fully-typed Python library for interacting with the Revolut X Crypto Exchange API.

## Features

- **Ed25519 Authentication** — secure request signing for private API endpoints
- **Public Market Data** — real-time tickers, order book, OHLCV candles, and public trades
- **Trading** — market and limit orders with post-only (maker) support
- **Account Management** — balances, transaction ledger, private trade history
- **Automatic Pagination** — `iter_candles()` and `iter_trades()` stream large datasets transparently
- **Utility Helpers** — `FeeCalculator` and `OrderPayloadBuilder` for easier integration
- **Type Hints & IDE Autocompletion** — TypedDicts, Enums, and full type annotations
- **Comprehensive Error Handling** — structured exception hierarchy (`RevolutXError` → `ApiError`, `AuthenticationError`, …)

## Documentation

Full interactive documentation (with API reference and guides) is powered by **MkDocs (Ivory theme)**:

- **Local Preview**: `cd python && mkdocs serve`
- **Build Static HTML**: `cd python && mkdocs build`
- **Deploy to GitHub Pages**: `cd python && mkdocs gh-deploy`

## Quick Start

### Public Data (No Authentication Required)

```python
from revolut_x import RevolutXClient, Interval

client = RevolutXClient()

# Get latest ticker for Bitcoin
ticker = client.get_ticker("BTC-EUR")
print(f"BTC Price: {ticker['last_price']} EUR")

# Get hourly candles
candles = client.get_candles("BTC-EUR", Interval.HOUR_1, since=1700000000000)
for candle in candles[:5]:
    print(f"Time: {candle['start']}, Close: {candle['close']}")
```

### Trading and Account (Authentication Required)

```python
from revolut_x import RevolutXClient, OrderSide

client = RevolutXClient(
    api_key="your-api-key",
    private_key_path="keys/private.pem",
)

# Get account balances
balances = client.get_balances()
for b in balances:
    if float(b["total"]) > 0:
        print(f"{b['currency']}: {b['available']} available")

# Place a market buy order (spend 50 EUR on BTC)
order = client.place_market_order(
    "BTC-EUR", OrderSide.BUY, quote_size="50.00"
)
print(f"Order ID: {order['venue_order_id']}")

# Place a post-only limit order (0% maker fee)
limit_order = client.place_limit_order(
    "BTC-EUR", OrderSide.SELL,
    price="90000.00",
    base_size="0.001",
    post_only=True,
)
print(f"Limit order: {limit_order['venue_order_id']}")
```

## Authentication Setup

Revolut X uses Ed25519 keys for request authentication.

1. **Generate Key Pair**:
   ```bash
   openssl genpkey -algorithm ed25519 -out keys/private.pem
   openssl pkey -in keys/private.pem -pubout -out keys/public.pem
   ```
2. **Register Public Key**: Go to your [Revolut X account settings](https://revx.revolut.com), create a new API key, and upload your `public.pem`.
3. **Use in SDK**: Pass the API key and private key path to `RevolutXClient`:
   ```python
   client = RevolutXClient(
       api_key="your-api-key",
       private_key_path="keys/private.pem",
   )
   ```

## API Reference

### Market Data (no authentication)

```python
client = RevolutXClient()

# Configuration
pairs = client.get_pairs()                    # dict[str, PairConfig]
pair = client.get_pair("BTC-EUR")             # PairConfig
currencies = client.get_currencies()          # dict[str, CurrencyConfig]

# Tickers & Order Book
tickers = client.get_tickers()                # list[Ticker]
ticker = client.get_ticker("BTC-EUR")         # Ticker
book = client.get_order_book("BTC-EUR", depth=10)  # OrderBook

# Candles (OHLCV)
candles = client.get_candles("BTC-EUR", Interval.HOUR_1,
                             since=1700000000000)  # list[Candle]

# Automatic pagination (generator)
for candle in client.iter_candles("BTC-EUR", Interval.MIN_1,
                                  since=1700000000000):
    process(candle)

# Public Trades
trades, next_cursor = client.get_trades("BTC-EUR", limit=100)

for trade in client.iter_trades("BTC-EUR", start_date=1700000000000):
    process(trade)
```

### Orders (authentication required)

```python
from revolut_x import OrderSide, TimeInForce

# Place orders
market = client.place_market_order("BTC-EUR", OrderSide.BUY, quote_size="50.00")
limit = client.place_limit_order("BTC-EUR", OrderSide.SELL,
                                  price="90000.00", base_size="0.001",
                                  post_only=True, time_in_force=TimeInForce.GTC)

# Raw payload via OrderPayloadBuilder
from revolut_x.helpers import OrderPayloadBuilder
payload = OrderPayloadBuilder.build_market_order("BTC-EUR", OrderSide.BUY,
                                                  quote_size="50.00")
result = client.place_order(payload)

# Query orders
detail = client.get_order("venue-order-uuid")
fills = client.get_order_fills("venue-order-uuid")
active = client.get_active_orders(symbol="BTC-EUR")
history, cursor = client.get_historical_orders(limit=50)

# Cancel orders
client.cancel_order("venue-order-uuid")
client.cancel_all_orders(symbol="BTC-EUR")  # symbol is optional
```

### Account (authentication required)

```python
balances = client.get_balances()                        # list[Balance]
eur = client.get_balance("EUR")                         # Balance
txns, cursor = client.get_transactions(limit=10)        # list[dict], cursor
trades, cursor = client.get_account_trades("BTC-EUR")   # list[Trade], cursor
```

### Helpers

```python
from revolut_x import FeeCalculator, OrderSide
from revolut_x.helpers import OrderPayloadBuilder

# Build and validate a payload
payload = OrderPayloadBuilder.build_limit_order(
    "BTC-EUR", OrderSide.BUY, price="85000.00", quote_size="50.00"
)
pair_rules = client.get_pair("BTC-EUR")
is_valid, errors = OrderPayloadBuilder.validate_against_pair_rules(payload, pair_rules)

# Estimate fees
fee = FeeCalculator.calculate(
    side=OrderSide.BUY,
    price="85000.00",
    is_maker=True,       # post_only → maker (0.00%)
    quote_size="50.00",
)
print(fee.explanation)
```

## Error Handling

```python
from revolut_x.exceptions import (
    RevolutXError,        # base for all library errors
    AuthenticationError,  # 401/403 or missing credentials
    RateLimitError,       # 429 after max retries
    ApiError,             # other 4xx/5xx
    OrderValidationError, # client-side payload validation
    NetworkError,         # connection/timeout failures
)

try:
    client.place_market_order("BTC-EUR", OrderSide.BUY, quote_size="50.00")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
    if e.hint:
        print(f"Hint: {e.hint}")
except ApiError as e:
    print(f"API Error (HTTP {e.status_code}): {e.response_body}")
except RevolutXError as e:
    print(f"SDK Error: {e}")
```

## Types & Enums

| Enum | Values |
|------|--------|
| `OrderSide` | `BUY`, `SELL` |
| `OrderType` | `MARKET`, `LIMIT` |
| `Interval` | `MIN_1`, `MIN_5`, `MIN_15`, `MIN_30`, `HOUR_1`, `HOUR_4`, `DAY_1`, `DAY_2`, `DAY_4`, `WEEK_1`, `WEEK_2`, `WEEK_4` |
| `TimeInForce` | `GTC` (good 'til canceled), `IOC` (immediate or cancel) |

TypedDicts for IDE autocompletion: `Candle`, `Trade`, `Ticker`, `Balance`, `PairConfig`, `CurrencyConfig`, `OrderBook`, `OrderResponse`, `OrderDetail`, `Fill`.

## Academic Reference / Diplomová práce

Tato knihovna vznikla jako součást **diplomové práce** na **VŠB – Technické univerzitě Ostrava** (Fakulta elektrotechniky a informatiky).

- **Instituce**: VŠB – Technická univerzita Ostrava (VŠB-TUO)
- **Fakulta**: Fakulta elektrotechniky a informatiky (FEI)
- **Typ práce**: Diplomová práce / Master's Thesis
- **Autor**: Bc. Jan Přikryl

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
