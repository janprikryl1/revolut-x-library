<?php

declare(strict_types=1);

namespace RevolutX\Tests;

use RevolutX\Exceptions\OrderValidationException;
use RevolutX\Helpers\FeeCalculator;
use RevolutX\Types\OrderSide;
use PHPUnit\Framework\TestCase;

class FeeCalculatorTest extends TestCase
{
    public function testCalculateMakerBuyZeroFee(): void
    {
        $estimate = FeeCalculator::calculate(
            side: OrderSide::BUY,
            price: '90000.00',
            isMaker: true,
            quoteSize: '1000.00'
        );

        $this->assertTrue($estimate->isMaker);
        $this->assertSame('0.00', $estimate->feeRatePercent);
        $this->assertSame('0.0000', $estimate->feeAmount);
        $this->assertSame('1000.00', $estimate->tradeValueEur);
        $this->assertSame('EUR', $estimate->feeCurrency);
        $this->assertSame('BTC', $estimate->netReceivedCurrency);
        $this->assertStringContainsString('MAKER', $estimate->explanation);
    }

    public function testCalculateTakerBuyFee(): void
    {
        // 1000 EUR trade at 90000 EUR/BTC, taker fee = 0.09% (0.90 EUR)
        $estimate = FeeCalculator::calculate(
            side: OrderSide::BUY,
            price: '90000.00',
            isMaker: false,
            quoteSize: '1000.00'
        );

        $this->assertFalse($estimate->isMaker);
        $this->assertSame('0.09', $estimate->feeRatePercent);
        $this->assertSame('0.9000', $estimate->feeAmount);
        $this->assertSame('EUR', $estimate->feeCurrency);
        $this->assertSame('0.01111111', $estimate->estimatedBaseQty);
    }

    public function testCalculateMakerSellZeroFee(): void
    {
        $estimate = FeeCalculator::calculate(
            side: OrderSide::SELL,
            price: '80000.00',
            isMaker: true,
            baseSize: '0.1'
        );

        $this->assertTrue($estimate->isMaker);
        $this->assertSame('0.00', $estimate->feeRatePercent);
        $this->assertSame('0.0000', $estimate->feeAmount);
        $this->assertSame('8000.00', $estimate->tradeValueEur);
        $this->assertSame('8000.00', $estimate->netReceived);
        $this->assertSame('EUR', $estimate->netReceivedCurrency);
    }

    public function testCalculateTakerSellFee(): void
    {
        // 0.1 BTC at 80000 EUR/BTC = 8000 EUR gross, taker fee 0.09% = 7.20 EUR
        // Net received = 8000 - 7.20 = 7992.80 EUR
        $estimate = FeeCalculator::calculate(
            side: OrderSide::SELL,
            price: '80000.00',
            isMaker: false,
            baseSize: '0.1'
        );

        $this->assertFalse($estimate->isMaker);
        $this->assertSame('0.09', $estimate->feeRatePercent);
        $this->assertSame('7.2000', $estimate->feeAmount);
        $this->assertSame('7992.80', $estimate->netReceived);
    }

    public function testCalculateThrowsWithoutSizes(): void
    {
        $this->expectException(OrderValidationException::class);
        FeeCalculator::calculate(OrderSide::BUY, '80000.00', true);
    }
}
