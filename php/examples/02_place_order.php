<?php

declare(strict_types=1);

require_once __DIR__ . '/../vendor/autoload.php';

use RevolutX\Client;
use RevolutX\Types\OrderSide;
use RevolutX\Types\OrderType;

$apiKey = getenv('REVX_API_KEY') ?: 'your-api-key';
$privateKeyPath = getenv('REVX_PRIVATE_KEY_PATH') ?: __DIR__ . '/../keys/private.pem';

// Initialize authenticated client
$client = new Client(
    apiKey: $apiKey,
    privateKeyPath: $privateKeyPath
);

if (!$client->isAuthenticated()) {
    echo "Client is not authenticated. Please set REVX_API_KEY and REVX_PRIVATE_KEY_PATH.\n";
    exit(1);
}

try {
    // 1. Check EUR balance
    $eur = $client->getBalance('EUR');
    echo "EUR Available: " . $eur['available'] . "\n";

    // 2. Submit a market buy order for 50 EUR
    $order = $client->placeMarketOrder(
        symbol: 'BTC-EUR',
        side: OrderSide::BUY,
        quoteSize: '50.00'
    );
    echo "Market order submitted! Venue Order ID: " . $order['venue_order_id'] . "\n";
} catch (\Throwable $e) {
    echo "Order failed: " . $e->getMessage() . "\n";
}
