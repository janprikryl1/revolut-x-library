# Revolut X Python SDK

Python client library for the **Revolut X Crypto Exchange REST API (v1.0)**.

📖 **Documentation**: [janprikryl1.github.io/revolut-x-python](https://janprikryl1.github.io/revolut-x-python/)  
🐘 **Looking for PHP?** See [revolut-x-php](https://github.com/janprikryl1/revolut-x-php).

---

## Features

- **Revolut X API v1.0** — Complete coverage of market data, order placement, balances, and transaction history.
- **Ed25519 Authentication** — Cryptographic request signing using `cryptography` (PKCS#8 PEM).
- **Smart Maker Strategy (0.00% fee)** — Automatic offset pricing and `post_only` execution to prevent taker fees (0.09%).
- **Streaming Iterators** — `iter_candles()` and `iter_trades()` automatically handle cursor pagination and rate-limit delays.
- **100% Type Annotated** — Built with Python `TypedDict`, `Enum`, and type annotations.
- **AI Agent Skill** — Pre-packaged skill definition for AI coding assistants (Google Antigravity, Claude, Cursor).

---

## Installation

```bash
pip install revolut-x-python
```

Or install in development mode from source:

```bash
pip install -e ".[dev,docs]"
```

---

## Quickstart

### 1. Public Market Data (No API Key Required)

```python
from revolut_x import RevolutXClient, Interval

client = RevolutXClient()

# Get BTC-EUR ticker
ticker = client.get_ticker("BTC-EUR")
print(f"BTC Price: {ticker['last_price']} EUR")

# Get 1-hour OHLCV candles
candles = client.get_candles("BTC-EUR", Interval.HOUR_1)
```

### 2. Authenticated Trading & 0% Fee Maker Orders

```python
from revolut_x import RevolutXClient, OrderSide

client = RevolutXClient(
    api_key="your-api-key",
    private_key_path="keys/private.pem",
)

# Submit zero-fee Maker limit order (post_only=True)
order = client.place_maker_order(
    symbol="BTC-EUR",
    side=OrderSide.BUY,
    quote_size="50.00",
    offset="0.10",
)
print(f"Order ID: {order['venue_order_id']}")
```

---

## Running Tests

```bash
pytest tests
```

---

## Academic Reference

Tato knihovna vznikla jako součást **diplomové práce** na **VŠB – Technické univerzitě Ostrava** (Fakulta elektrotechniky a informatiky).

- **Autor**: Bc. Jan Přikryl
- **Univerzita**: VŠB – Technická univerzita Ostrava
- **Fakulta**: Fakulta elektrotechniky a informatiky (FEI)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
