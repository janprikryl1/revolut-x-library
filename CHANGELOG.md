# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-10

Correctness release. Two public methods were unusable as shipped, and several
declared types did not match what the exchange actually returns. Every item
below was verified against the live Revolut X API.

### Fixed
- **`iter_candles()` crashed on page-aligned ranges**: any window that was an
  exact multiple of 1000 candles ended with a request where `since == until`,
  which the exchange rejects with HTTP 400 (`Invalid interval: 'until' is
  before 'since'`). Windows of 1000/2000/3000 candles failed; 999/1500 worked.
  Pagination now walks fixed windows forward instead of chaining off the last
  returned candle, which also makes it immune to gaps in the series (an
  illiquid pair with no trades in an interval used to end iteration early).
  Guaranteed: no candle yielded twice, none past `until`.
- **`get_trades()` / `iter_trades()` failed out of the box**: the default
  `limit` was 1900, but `/public/trades/all` accepts only **1–100** and rejects
  anything larger with HTTP 400 (`Limit must be between 1 and 100`). The
  default is now 100 and out-of-range values are clamped into the accepted
  range.
- **Query parameters are now sorted before being sent**: the canonical
  signature message sorts them alphabetically, while `requests` serialised them
  in insertion order, so the signed string and the string on the wire could
  differ for authenticated paginated calls (`get_historical_orders`,
  `get_transactions`, `get_account_trades` when a `cursor` was present).

### Changed
- **`OrderBook` type corrected**: levels are dictionaries, **not**
  `[price, quantity]` pairs. Added `OrderBookLevel` (exported from
  `revolut_x`) documenting all 13 fields the venue returns; read the price from
  `['p']` and the quantity from `['q']`. The previous shape made every
  documented order-book example raise `KeyError` or `ValueError`.
- **`Ticker` type corrected**: `high`, `low` and `volume` do not exist in the
  response — the real fields are `high_24h`, `low_24h` and `volume_24h`. Added
  the missing `mid`, `index_price`, `price_change_24h`, `quote_volume_24h` and
  `region`.
- **`Trade` type**: added the `region` field returned by the API.
- **`get_order_book(depth=...)`**: documented that the exchange currently
  ignores this argument and always returns 5 levels per side. The parameter is
  kept so deeper books are picked up automatically if that changes.
- **`get_candles()` docstring**: a window wider than 1000 candles is a hard
  HTTP 400, not a silent truncation. The previous example (`since` three years
  in the past) could not succeed.
- **Single source of truth for the version**: `pyproject.toml`,
  `revolut_x.__version__` and the default `User-Agent` now all resolve to
  `revolut_x._version.__version__`. They had drifted to three different values
  (0.0.8 / 0.0.6 / 0.1.0 respectively).
- **Documentation**: translated the remaining Czech text in the English guides
  (`index.md`, `concepts/auth_ed25519.md`, `concepts/maker_strategy.md`,
  `guide/market_data.md`) left over from the i18n migration.
- **AI Agent Skill**: corrected the order-book and ticker shapes in
  `.agents/skills/revolut-x-library/`, which had been teaching assistants the
  wrong field names.

### Added
- **Tests**: `tests/test_market.py` — 7 tests covering candle pagination
  (page-aligned windows, exact range coverage, no overshoot past `until`, gap
  tolerance), the trades `limit` bound, and order-book pass-through. The suite
  is now 43 tests.

---

## [0.0.8] - 2026-10-05

### Added
- **Timestamp synchronisation**: `sync_time()` derives a clock offset from the
  server `Date` header, with automatic drift correction on HTTP 409 and a
  `timestamp_offset_ms` client option, so request signing survives a skewed
  local clock ([`d9c5127`](https://github.com/janprikryl1/revolut-x-library/commit/d9c5127)).

---

## [0.0.7] - 2026-10-05

### Changed
- **Repository restructured**: the Python SDK moved from `python/` to the
  repository root (`src/`, `tests/`, `examples/`), so the package builds from
  the top level ([`52af8e3`](https://github.com/janprikryl1/revolut-x-library/commit/52af8e3)).
- **PHP SDK removed** from this repository; it now lives in
  [revolut-x-php](https://github.com/janprikryl1/revolut-x-php).

### Added
- **Unified multi-language documentation**: MkDocs site with English and Czech
  (`mkdocs-static-i18n`, Material theme), shared protocol concepts
  (`docs/concepts/auth_ed25519.md`, `docs/concepts/maker_strategy.md`), and a
  GitHub Actions workflow deploying to GitHub Pages.
- **AI Agent Skill**: skill definition and types reference
  (`.agents/skills/revolut-x-library/`) for AI coding assistants
  ([`c586fef`](https://github.com/janprikryl1/revolut-x-library/commit/c586feffa491bfde7c63b891893746c9571cd68d)).

## [0.0.6] - 2026-09-29

### Added
- **Smart Maker Order Strategy**: Added support for zero-fee Maker orders with dynamic offset pricing (`MakerOrderStrategy`) to prevent unintentional taker fees ([`f65686c`](https://github.com/janprikryl1/revolut-x-library/commit/f65686c9553cde642a3fdafc3bb9f05dcd4a092b)).
- **Example**: Added `python/examples/06_smart_maker_orders.py` showcasing zero-fee maker order placement and offset calculation.
- **Tests**: Added unit test suite `python/tests/test_maker_strategy.py`.
- **Documentation**: Updated order documentation in `python/docs/guide/orders.md` with maker strategy guidelines.

---

## [0.0.5] - 2026-09-29

### Fixed
- **Documentation**: Fixed and refined documentation across `python/README.md` and `python/docs/index.md` ([`7fd5100`](https://github.com/janprikryl1/revolut-x-library/commit/7fd5100b8826ce4e126f17a251e76165e2939930)).

---

## [0.0.4] - 2026-09-29

### Changed
- **API Alignment**: Renamed client methods for full consistency with the Revolut X Crypto Exchange API v1.0 specifications and Python conventions ([`37d1e03`](https://github.com/janprikryl1/revolut-x-library/commit/37d1e032cb6a5379a181e52432b61b87f384244e)).
- **Documentation**: Added explicit references to Revolut X API v1.0 throughout docstrings and documentation.

### Added
- **Tests**: Added dedicated orders unit test suite `python/tests/test_orders.py`.

---

## [0.0.3] - 2026-09-28

### Added
- **Packaging**: First release uploaded to TestPyPI ([`4471e7e`](https://github.com/janprikryl1/revolut-x-library/commit/4471e7efb6f964ea571e7a6d9735e9e66cd1cc21)).
- **Monorepo Structure**: Added root `README.md` describing multi-language SDK layout.
- **Type Information**: Added PEP 561 `py.typed` marker file for strict type checking support.

### Changed
- **Package Layout**: Migrated Python package to modern `src/` layout (`python/src/revolut_x/`).
- **Dependencies**: Configured optional dependencies (`dev`, `docs`) in `pyproject.toml`.

---

## [0.0.2] - 2026-09-28

### Added
- **CI/CD**: Added GitHub Actions workflow (`.github/workflows/docs.yml`) for automated MkDocs documentation build and GitHub Pages deployment ([`ae145d0`](https://github.com/janprikryl1/revolut-x-library/commit/ae145d0b7b2448e29280e904c27ae0c96eccf20d)).

### Fixed
- **CI/CD**: Fixed Python directory paths in the GitHub Actions documentation deployment workflow ([`a220efd`](https://github.com/janprikryl1/revolut-x-library/commit/a220efd650652765f30e26d146a344a4736b41d0)).
- **Repository Metadata**: Corrected repository display name in `mkdocs.yml` ([`c33a065`](https://github.com/janprikryl1/revolut-x-library/commit/c33a0655d4584cb534e758f3d380b110333f5c33)).

---

## [0.0.1] - 2026-09-28

### Added
- **Initial Implementation**: Initial commit of the Revolut X Crypto Exchange REST API Python SDK ([`c6857a5`](https://github.com/janprikryl1/revolut-x-library/commit/c6857a5e2ddc1f5da5d3cb02092bbf339ac7579e)).
  - **Client (`RevolutXClient`)**: Main client supporting both public and authenticated endpoints.
  - **Authentication (`_auth.py`)**: Ed25519 cryptographic request signing using private keys.
  - **HTTP Transport (`_http.py`)**: Robust HTTP session layer with request signing and error handling.
  - **Market Data API (`market.py`)**: Endpoints for tickers, order books, OHLCV candles, and public trades.
  - **Account API (`account.py`)**: Balances retrieval and account configuration.
  - **Orders API (`orders.py`)**: Placing limit and market orders, order cancellation, and querying active/historical orders.
  - **Helpers (`helpers.py`)**: Fee calculation utilities (Maker vs Taker), precision helpers, and payload validation.
  - **Data Types (`types.py`)**: Type definitions and enums (`OrderSide`, `OrderType`, `TimeInForce`, `Interval`).
  - **Error Handling (`exceptions.py`)**: Structured exception hierarchy (`AuthenticationError`, `RateLimitError`, `APIError`, etc.).
  - **Examples**: Example scripts covering public data, candle streams, account history, orders, and fee calculation.
  - **Unit Tests**: Test suites for authentication and helper functions (`test_auth.py`, `test_helpers.py`).
  - **Documentation**: Complete MkDocs documentation site setup with guides and API references.
