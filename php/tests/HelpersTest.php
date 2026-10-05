<?php

declare(strict_types=1);

namespace RevolutX\Tests;

use RevolutX\Exceptions\OrderValidationException;
use RevolutX\Helpers\OrderPayloadBuilder;
use RevolutX\Helpers\SymbolNormalizer;
use RevolutX\Types\OrderSide;
use RevolutX\Types\OrderType;
use RevolutX\Types\TimeInForce;
use PHPUnit\Framework\TestCase;

class HelpersTest extends TestCase
{
    public function testNormalizeSymbol(): void
    {
        $this->assertSame('BTC-EUR', SymbolNormalizer::normalize('BTC/EUR'));
        $this->assertSame('BTC-EUR', SymbolNormalizer::normalize('BTC-EUR'));
        $this->assertSame('BTC-EUR', SymbolNormalizer::normalize('btceur'));
        $this->assertSame('BTC-EUR', SymbolNormalizer::normalize('BTCEUR'));
        $this->assertSame('ETH-USDC', SymbolNormalizer::normalize('ethusdc'));
        $this->assertSame('SOL-USD', SymbolNormalizer::normalize('SOLUSD'));
    }

    public function testBuildMarketOrderValid(): void
    {
        $payload = OrderPayloadBuilder::buildMarketOrder(
            symbol: 'BTC/EUR',
            side: OrderSide::BUY,
            quoteSize: '50.00',
            clientOrderId: 'custom-uuid-123'
        );

        $this->assertSame('custom-uuid-123', $payload['client_order_id']);
        $this->assertSame('BTC-EUR', $payload['symbol']);
        $this->assertSame('buy', $payload['side']);
        $this->assertSame(['quote_size' => '50.00'], $payload['order_configuration']['market']);
    }

    public function testBuildMarketOrderThrowsIfBothOrNeitherSizes(): void
    {
        $this->expectException(OrderValidationException::class);
        OrderPayloadBuilder::buildMarketOrder('BTC-EUR', OrderSide::BUY);
    }

    public function testBuildLimitOrderValid(): void
    {
        $payload = OrderPayloadBuilder::buildLimitOrder(
            symbol: 'BTC-EUR',
            side: OrderSide::SELL,
            price: '90000.00',
            baseSize: '0.005',
            postOnly: true,
            timeInForce: TimeInForce::GTC
        );

        $this->assertSame('BTC-EUR', $payload['symbol']);
        $this->assertSame('sell', $payload['side']);
        $limitConf = $payload['order_configuration']['limit'];
        $this->assertSame('90000.00', $limitConf['price']);
        $this->assertSame('0.005', $limitConf['base_size']);
        $this->assertSame(['post_only'], $limitConf['execution_instructions']);
        $this->assertSame('gtc', $limitConf['time_in_force']);
    }

    public function testBuildMakerOrderShortcut(): void
    {
        $payload = OrderPayloadBuilder::buildMakerOrder(
            symbol: 'BTC-EUR',
            side: OrderSide::BUY,
            price: '85000.00',
            quoteSize: '100.00'
        );

        $limitConf = $payload['order_configuration']['limit'];
        $this->assertSame(['post_only'], $limitConf['execution_instructions']);
        $this->assertSame('85000.00', $limitConf['price']);
    }

    public function testValidateAgainstPairRules(): void
    {
        $rules = [
            'min_order_size' => '0.0001',
            'max_order_size' => '10.0',
            'min_order_size_quote' => '5.0',
            'max_order_size_quote' => '100000.0',
        ];

        // Valid order
        $validPayload = OrderPayloadBuilder::buildMarketOrder('BTC-EUR', OrderSide::BUY, quoteSize: '50.0');
        [$ok, $errors] = OrderPayloadBuilder::validateAgainstPairRules($validPayload, $rules);
        $this->assertTrue($ok);
        $this->assertEmpty($errors);

        // Below minimum quote size
        $invalidPayload = OrderPayloadBuilder::buildMarketOrder('BTC-EUR', OrderSide::BUY, quoteSize: '1.0');
        [$okInvalid, $errorsInvalid] = OrderPayloadBuilder::validateAgainstPairRules($invalidPayload, $rules);
        $this->assertFalse($okInvalid);
        $this->assertNotEmpty($errorsInvalid);
    }
}
