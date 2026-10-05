# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **PHP SDK (`php/`)**: Initial implementation of the Revolut X Crypto Exchange REST API PHP SDK (`janprikryl/revolutx`):
  - **Client (`Client` / `RevolutXClient`)**: Unified client combining public and authenticated endpoints.
  - **Ed25519 Authentication (`Signer`)**: Native cryptographic request signing using PHP's `ext-sodium`.
  - **HTTP Transport (`HttpClient`)**: Native cURL layer with automatic rate limiting (1 req/s), 429 retry backoff, and exception mapping.
  - **Market API (`MarketTrait`)**: Endpoints for pairs, currencies, tickers, order book, OHLCV candles, and public trades.
  - **Orders API (`OrdersTrait`)**: Market/Limit order execution, order fills, active and historical order querying, and cancellation.
  - **Account API (`AccountTrait`)**: Account balances, ledger transaction history, and private trade history.
  - **Helpers (`MakerOrderStrategy`, `FeeCalculator`, `OrderPayloadBuilder`, `SymbolNormalizer`)**: 0% Maker fee calculation, order payload validation, and symbol normalization.
  - **Types & Enums (`Types/`)**: Class-based enums compatible with PHP 8.0+ (`OrderSide`, `OrderType`, `TimeInForce`, `Interval`) and `FeeEstimate` DTO.
  - **Structured Exceptions (`Exceptions/`)**: Full exception hierarchy (`AuthenticationException`, `RateLimitException`, `ApiException`, `OrderValidationException`, `NetworkException`).
  - **Unit Tests (`tests/`)**: Complete test suite using PHPUnit covering authentication, builders, maker strategy, fee math, and client behavior (28 tests, 81 assertions).
  - **Examples (`examples/`)**: Executable scripts demonstrating public data, order placement, maker strategy, and fee calculations.
- **Unified Multi-Language Documentation**:
  - Centralized documentation from `python/` to repository root (`docs/`, `mkdocs.yml`) covering both Python and PHP SDKs on a single GitHub Pages website.
  - Added comprehensive PHP guides (Quickstart, Market Data, Orders, Account, Maker Strategy, API Reference).
  - Added shared API and protocol concepts (`docs/concepts/auth_ed25519.md`, `docs/concepts/maker_strategy.md`).
  - Updated GitHub Actions workflow (`.github/workflows/docs.yml`) to build and deploy the unified documentation on GitHub Pages.
- **AI Agent Skill**: Added Antigravity / AI Agent integration skill definition and types reference (`.agents/skills/revolut-x-library/`) for automated market interaction and coding assistance ([`c586fef`](https://github.com/janprikryl1/revolut-x-library/commit/c586feffa491bfde7c63b891893746c9571cd68d)).
- **Documentation**: Added AI Agent Integration guide (`docs/ai_agents.md`) and updated MkDocs navigation.

---

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
