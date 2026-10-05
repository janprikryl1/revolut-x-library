<?php

declare(strict_types=1);

namespace RevolutX\Tests;

use RevolutX\Exceptions\OrderValidationException;
use RevolutX\Helpers\MakerOrderStrategy;
use RevolutX\Types\OrderSide;
use PHPUnit\Framework\TestCase;

class MakerStrategyTest extends TestCase
{
    public function testCalculateMakerPriceBuyWithBestBid(): void
    {
        // For BUY: best_bid - offset
        $price = MakerOrderStrategy::calculateMakerPrice(
            side: OrderSide::BUY,
            bestBid: '80000.00',
            offset: '0.10',
            tickSize: '0.01'
        );

        $this->assertSame('79999.90', $price);
    }

    public function testCalculateMakerPriceSellWithBestAsk(): void
    {
        // For SELL: best_ask + offset
        $price = MakerOrderStrategy::calculateMakerPrice(
            side: OrderSide::SELL,
            bestAsk: '80000.50',
            offset: '0.10',
            tickSize: '0.01'
        );

        $this->assertSame('80000.60', $price);
    }

    public function testCalculateMakerPriceFallbackLastPrice(): void
    {
        $price = MakerOrderStrategy::calculateMakerPrice(
            side: 'buy',
            bestBid: null,
            lastPrice: '75000.00',
            offset: '1.00',
            tickSize: '0.50'
        );

        $this->assertSame('74999.00', $price);
    }

    public function testCalculateMakerPriceThrowsWithoutReferencePrice(): void
    {
        $this->expectException(OrderValidationException::class);
        MakerOrderStrategy::calculateMakerPrice(
            side: OrderSide::BUY,
            bestBid: null,
            lastPrice: null
        );
    }

    public function testCalculateMakerPriceThrowsWithInvalidSide(): void
    {
        $this->expectException(OrderValidationException::class);
        MakerOrderStrategy::calculateMakerPrice(
            side: 'invalid_side',
            bestBid: '80000.00'
        );
    }
}
