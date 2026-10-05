<?php

declare(strict_types=1);

require_once __DIR__ . '/../vendor/autoload.php';

use RevolutX\Client;
use RevolutX\Types\Interval;

// 1. Initialize public client (no API keys required)
$client = new Client();

echo "=== 1. Fetching Ticker for BTC-EUR ===\n";
try {
    $ticker = $client->getTicker('BTC-EUR');
    echo "Last Price: " . ($ticker['last_price'] ?? 'N/A') . " EUR\n";
    echo "Best Bid:   " . ($ticker['bid'] ?? 'N/A') . " EUR\n";
    echo "Best Ask:   " . ($ticker['ask'] ?? 'N/A') . " EUR\n";
} catch (\Throwable $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

echo "\n=== 2. Fetching Order Book (Depth: 5) ===\n";
try {
    $book = $client->getOrderBook('BTC-EUR', depth: 5);
    echo "Bids count: " . count($book['bids'] ?? []) . "\n";
    echo "Asks count: " . count($book['asks'] ?? []) . "\n";
} catch (\Throwable $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

echo "\n=== 3. Fetching 1-Hour Candles ===\n";
try {
    $candles = $client->getCandles('BTC-EUR', Interval::HOUR_1);
    echo "Candles count: " . count($candles) . "\n";
} catch (\Throwable $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
