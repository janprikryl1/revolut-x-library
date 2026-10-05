# Revolut X PHP SDK

PHP client library for interacting with the **Revolut X Crypto Exchange REST API (v1.0)**.

Designed for PHP 8.0+ / 8.1+ with strict typing, zero external runtime dependencies, built-in Ed25519 cryptographic signing (`ext-sodium`), automated rate-limiting, and 0% Maker fee optimization.

---

## Features

- **Revolut X API v1.0** — Full endpoint coverage: market data, order execution, balances, and transaction history.
- **Ed25519 Authentication** — Cryptographic request signing using PHP's native `ext-sodium`.
- **Zero Runtime Dependencies** — Uses PHP built-in extensions (`ext-curl`, `ext-sodium`, `ext-json`).
- **PHP 8.0+ Compatible** — Tested on PHP 8.0 through PHP 8.5 with strict types and class-based enums.
- **Maker Order Strategy** — Dynamic offset pricing guaranteeing entry as Maker (0.00% fee).
- **Automated Rate Limiting** — Transparent request delay handling conforming to Revolut X public API limits (1 req/sec) and HTTP 429 retries.
- **Structured Exceptions** — Hierarchical exception tree (`AuthenticationException`, `RateLimitException`, `ApiException`, `OrderValidationException`).

---

## Requirements

- PHP `^8.0` (PHP 8.0.30+, 8.1, 8.2, 8.3, 8.4, 8.5)
- Extensions: `ext-curl`, `ext-json`, `ext-sodium`

---

## Installation

```bash
composer require janprikryl/revolutx
```

Or clone and autoload via Composer:

```bash
cd php
composer install
```

---

## Quickstart

### 1. Public Market Data (No API keys required)

```php
use RevolutX\Client;
use RevolutX\Types\Interval;

$client = new Client();

// 1. Get current BTC-EUR ticker
$ticker = $client->getTicker('BTC-EUR');
echo "BTC Price: " . $ticker['last_price'] . " EUR\n";

// 2. Fetch order book (top 5 bids and asks)
$orderBook = $client->getOrderBook('BTC-EUR', depth: 5);

// 3. Fetch 1-hour OHLCV candles
$candles = $client->getCandles('BTC-EUR', Interval::HOUR_1);
```

### 2. Authenticated Trading & Balances

```php
use RevolutX\Client;
use RevolutX\Types\OrderSide;

$client = new Client(
    apiKey: 'your-api-key',
    privateKeyPath: 'path/to/private.pem'
);

// Check account balance
$eur = $client->getBalance('EUR');
echo "EUR Available: " . $eur['available'] . "\n";

// Place a market buy order for 50 EUR
$order = $client->placeMarketOrder(
    symbol: 'BTC-EUR',
    side: OrderSide::BUY,
    quoteSize: '50.00'
);
echo "Order ID: " . $order['venue_order_id'] . "\n";
```

### 3. Smart Maker Orders (0.00% Fee)

```php
use RevolutX\Client;
use RevolutX\Types\OrderSide;

// Automatically fetches the live book, applies offset, and submits post_only=true
$order = $client->placeMakerOrder(
    symbol: 'BTC-EUR',
    side: OrderSide::BUY,
    quoteSize: '50.00',
    offset: '0.10'
);
```

---

## Running Tests

```bash
cd php
./vendor/bin/phpunit
```

---

## License

MIT License. Part of diploma thesis at VŠB – Technical University of Ostrava.
