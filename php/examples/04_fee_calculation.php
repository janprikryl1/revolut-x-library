<?php

declare(strict_types=1);

require_once __DIR__ . '/../vendor/autoload.php';

use RevolutX\Helpers\FeeCalculator;
use RevolutX\Types\OrderSide;

echo "=== Fee Comparison: Maker (0.00%) vs Taker (0.09%) ===\n\n";

$tradeValueEur = '1000.00';
$price = '90000.00';

// 1. Taker Buy (Market Order)
$taker = FeeCalculator::calculate(
    side: OrderSide::BUY,
    price: $price,
    isMaker: false,
    quoteSize: $tradeValueEur
);
echo "[TAKER BUY]\n" . $taker->explanation . "\n\n";

// 2. Maker Buy (Limit Order with post_only=true)
$maker = FeeCalculator::calculate(
    side: OrderSide::BUY,
    price: $price,
    isMaker: true,
    quoteSize: $tradeValueEur
);
echo "[MAKER BUY]\n" . $maker->explanation . "\n";
