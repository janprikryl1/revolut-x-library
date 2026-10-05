# Revolut X Multi-Language Library

Multi-language SDK repository for interacting with the **Revolut X Crypto Exchange REST API** (API Version `1.0`).

📖 **Unified Documentation**: [janprikryl1.github.io/revolut-x-library](https://janprikryl1.github.io/revolut-x-library/)

---

## Available SDKs

| Language | Directory | Package / Status | Documentation | API Version |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | [`python/`](./python) | [`revolut-x-python`](./python) (`v0.0.6`) | [Python Docs](https://janprikryl1.github.io/revolut-x-library/python/quickstart/) | `1.0` |
| **PHP** | [`php/`](./php) | [`janprikryl/revolutx`](./php) (`v0.1.0`) | [PHP Docs](https://janprikryl1.github.io/revolut-x-library/php/quickstart/) | `1.0` |
| **TypeScript / Node.js** | `typescript/` | *Planned* | — | `1.0` |
| **Go** | `go/` | *Planned* | — | `1.0` |

---

## Quickstart

### Python SDK

```bash
cd python
pip install .
```

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

### PHP SDK

```bash
cd php
composer install
```

```php
use RevolutX\Client;
use RevolutX\Types\Interval;

// Public data client (no credentials required)
$client = new Client();

// Get BTC-EUR ticker
$ticker = $client->getTicker('BTC-EUR');
echo "BTC price: {$ticker['last_price']} EUR\n";

// Get 1-hour OHLCV candles
$candles = $client->getCandles('BTC-EUR', Interval::HOUR_1);
```

---

## Repository Structure

Each language implementation lives in its own root subdirectory and follows that ecosystem's standard packaging layout. Documentation is unified at the repository root and deployed via GitHub Pages:

```text
revolut-x-library/
├── .github/workflows/   # CI/CD and GitHub Pages deployment workflow
├── docs/                # Unified documentation for Python & PHP
├── mkdocs.yml           # Root MkDocs configuration
├── README.md            # Monorepo overview
├── CHANGELOG.md         # Monorepo changelog
│
├── python/              # Python SDK (PEP 517/621 src-layout)
│   ├── pyproject.toml
│   ├── README.md
│   ├── examples/
│   ├── src/revolut_x/
│   └── tests/
│
├── php/                 # PHP SDK (Composer PSR-4 layout)
│   ├── composer.json
│   ├── phpunit.xml
│   ├── README.md
│   ├── examples/
│   ├── src/
│   └── tests/
│
└── ...                  # Future language implementations
```

---

## Academic Reference

Tato knihovna vznikla jako součást **diplomové práce** na **VŠB – Technické univerzitě Ostrava** (Fakulta elektrotechniky a informatiky).

- **Autor**: Bc. Jan Přikryl
- **Univerzita**: VŠB – Technická univerzita Ostrava
- **Fakulta**: Fakulta elektrotechniky a informatiky (FEI)

---

## License

This project is licensed under the MIT License - see the [LICENSE](python/LICENSE) file for details.
