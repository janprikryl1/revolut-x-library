# Quick Start Guide

This guide walks you through setting up credentials, initializing `RevolutXClient`, and interacting with the exchange.

---

## Authentication Setup

Revolut X uses **Ed25519** cryptographic key pairs for request signing.

### 1. Generate an Ed25519 Key Pair

Run the following standard OpenSSL commands:

```bash
# Generate private key PEM
openssl genpkey -algorithm ed25519 -out keys/private.pem

# Extract public key PEM
openssl pkey -in keys/private.pem -pubout -out keys/public.pem
```

### 2. Register Your Public Key on Revolut X

1. Log into your [Revolut X Account](https://revx.revolut.com).
2. Navigate to **API Settings** and create a new API key.
3. Paste the contents of your `public.pem` file.
4. Copy the generated **API Key** string.

### 3. Store Credentials in `.env`

Create a `.env` file in your application root:

```ini
REVOLUT_API_KEY=your_api_key_here
REVOLUT_PRIVATE_KEY_PATH=keys/private.pem
```

---

## Initializing the Client

### Public Client (No Credentials)
When only accessing public market data (tickers, order books, candles, pair limits), you don't need credentials:

```python
from revolut_x import RevolutXClient

client = RevolutXClient()
print(client.is_authenticated)  # False
```

### Authenticated Client
To trade, cancel orders, or query balances, supply both the API key and the private key:

```python
from revolut_x import RevolutXClient

client = RevolutXClient(
    api_key="your_api_key_here",
    private_key_path="keys/private.pem",
)
print(client.is_authenticated)  # True
```