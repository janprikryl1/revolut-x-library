<?php

declare(strict_types=1);

require_once __DIR__ . '/../vendor/autoload.php';

use RevolutX\Client;
use RevolutX\Helpers\MakerOrderStrategy;
use RevolutX\Types\OrderSide;

$apiKey = getenv('REVX_API_KEY') ?: null;
$privateKeyPath = getenv('REVX_PRIVATE_KEY_PATH') ?: null;

$client = new Client(
    apiKey: $apiKey,
    privateKeyPath: $privateKeyPath
);

try {
    // 1. Fetch current ticker
    $ticker = $client->getTicker('BTC-EUR');
    $bestBid = $ticker['bid'];
    $bestAsk = $ticker['ask'];

    echo "Current Market:\n";
    echo "  Best Bid: {$bestBid} EUR\n";
    echo "  Best Ask: {$bestAsk} EUR\n\n";

    // 2. Calculate optimal maker buy price (best_bid - 0.10)
    $makerBuyPrice = MakerOrderStrategy::calculateMakerPrice(
        side: OrderSide::BUY,
        bestBid: $bestBid,
        offset: '0.10',
        tickSize: '0.01'
    );
    echo "Optimal Maker BUY limit price: {$makerBuyPrice} EUR (0.00% fee guaranteed)\n";

    // 3. Submit zero-fee Maker order automatically:
    // $order = $client->placeMakerOrder('BTC-EUR', OrderSide::BUY, quoteSize: '50.00');
    // echo "Maker Order ID: " . $order['venue_order_id'] . "\n";
} catch (\Throwable $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
