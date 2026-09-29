# Revolut X Python
<em>Python SDK for the Revolut X Crypto Exchange REST API (v1.0).</em>

---

## Key Highlights

- **API Version 1.0 Support** — Targets Revolut X REST API `1.0` with configurable versioning.
- **Ed25519 Authentication** — Industry-standard elliptic curve signing for private endpoints.
- **Comprehensive Market Data** — Live order books, real-time tickers, trading pair rules, OHLCV candlesticks, and tick-by-tick public trade feeds.
- **Automated Streaming Iterators** — `iter_candles()` and `iter_trades()` transparently handle cursor pagination and rate-limit windows.
- **Zero-Fee Trading Support** — First-class support for `post_only` Maker orders (0.00% fee).
- **Built-in Helpers** — `FeeCalculator` and `OrderPayloadBuilder` provide pre-submission rule validation and fee projections.
- **100% Type Annotated** — Built with Python `TypedDict`, `Enum`, and modern type annotations for autocomplete in VS Code and PyCharm.
- **Structured Exceptions** — Hierarchical error handling (`AuthenticationError`, `RateLimitError`, `ApiError`, `NetworkError`).

---

## Installation

```bash
pip install -i https://test.pypi.org/simple/ revolut-x-python
```

---

## Quick Example

```python
from revolut_x import RevolutXClient, OrderSide, Interval

# 1. Public Market Data (No API Key Required)
client = RevolutXClient()
ticker = client.get_ticker("BTC-EUR")
print(f"BTC Price: {ticker['last_price']} EUR")

# 2. Authenticated Trading
client = RevolutXClient(
    api_key="your_api_key_here",
    private_key_path="keys/private.pem",
)

# Submit a 0% fee limit buy order
order = client.place_limit_order(
    symbol="BTC-EUR",
    side=OrderSide.BUY,
    price="70000.00",
    quote_size="50.00",
    post_only=True,
)
print(f"Order ID: {order['venue_order_id']}")
```

---

## Reference

Tato knihovna vznikla jako součást **diplomové práce** na **VŠB – Technické univerzitě Ostrava** (Fakulta elektrotechniky a informatiky).

- VŠB – Technická univerzita Ostrava, fakulta elektrotechniky a informatiky
- **Typ práce**: Diplomová práce / Master's Thesis
- **Autor**: Bc. Jan Přikryl
