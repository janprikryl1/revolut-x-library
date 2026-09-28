# Revolut X Python SDK - Examples

This directory contains executable, well-documented examples demonstrating how to use the `revolut-x-python` SDK for market data analysis, trading, and account management.

---

## Prerequisites

Before running the examples, ensure the package is installed:

```bash
# In development (editable mode from repo root):
pip install -e revolut-x-library/python
```

For examples requiring authentication (`03_*` and `04_*`), ensure your `.env` file (or environment variables) contains your API key and private key path:

```env
REVOLUT_API_KEY=your_api_key_here
REVOLUT_PRIVATE_KEY_PATH=keys/private.pem
```

---

## Overview of Examples

| File | Authentication | Description |
|---|:---:|---|
| **[`01_public_market_data.py`](01_public_market_data.py)** | No | Fetching trading pairs, tickers, live order book, and recent trades. |
| **[`02_download_candles_stream.py`](02_download_candles_stream.py)** | No | Using `iter_candles()` to stream and paginate historical OHLCV candles across days. |
| **[`03_account_balances_and_history.py`](03_account_balances_and_history.py)** | Yes | Inspecting available/reserved balances, ledger transactions, and private trade history. |
| **[`04_place_and_cancel_orders.py`](04_place_and_cancel_orders.py)** | Yes | Submitting limit Maker orders (`post_only=True`), inspecting status, and canceling orders. |
| **[`05_fee_calculator_and_validation.py`](05_fee_calculator_and_validation.py)** | No | Simulating Maker (0.00%) vs Taker (0.09%) fees and validating payloads against pair limits. |
