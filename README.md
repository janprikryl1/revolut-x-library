# Revolut X Library

Multi-language SDK repository for interacting with the **Revolut X Crypto Exchange REST API**.

## Available SDKs

| Language | Directory | Package / Status | Documentation |
| :--- | :--- | :--- | :--- |
| **Python** | [`python/`](./python) | [`revolut-x-python`](./python) (`v0.1.0`) | [Python Docs](./python/docs) / [Read the Docs](#) |
| **TypeScript / Node.js** | `typescript/` | *Planned* | — |
| **Go** | `go/` | *Planned* | — |

---

## Python SDK Quickstart

For detailed Python SDK instructions, tests, and examples, see the [`python/`](./python) directory.

### Installation

```bash
cd python
pip install .
```

Or install in editable mode for development:

```bash
cd python
pip install -e ".[dev]"
```

### Basic Example

```python
from revolut_x import RevolutXClient, Interval

# Public data client (no credentials required)
client = RevolutXClient()

# Get BTC-EUR ticker
ticker = client.get_ticker("BTC-EUR")
print(f"BTC price: {ticker['last_price']} EUR")

# Get 1-hour OHLCV candles
candles = client.get_candles("BTC-EUR", Interval.HOUR_1)
```

---

## Repository Structure

Each language implementation lives in its own root subdirectory and follows that ecosystem's standard packaging layout:

```text
revolut-x-library/
├── .github/workflows/   # CI/CD and deployment workflows
├── README.md            # Monorepo overview
│
├── python/              # Python SDK (PEP 517/621 src-layout)
│   ├── pyproject.toml
│   ├── README.md
│   ├── docs/
│   ├── examples/
│   ├── src/
│   │   └── revolut_x/
│   └── tests/
│
└── ...                  # Future language implementations
```

## License

This project is licensed under the MIT License - see the [LICENSE](python/LICENSE) file for details.
