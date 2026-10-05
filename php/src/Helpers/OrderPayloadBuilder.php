<?php

declare(strict_types=1);

namespace RevolutX\Helpers;

use RevolutX\Exceptions\OrderValidationException;
use RevolutX\Types\OrderSide;
use RevolutX\Types\OrderType;
use RevolutX\Types\TimeInForce;

/**
 * Builder and validator for Revolut X API order payloads.
 */
class OrderPayloadBuilder
{
    public static function uuid4(): string
    {
        $data = random_bytes(16);
        $data[6] = chr(ord($data[6]) & 0x0f | 0x40);
        $data[8] = chr(ord($data[8]) & 0x3f | 0x80);
        return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
    }

    public static function formatDecimal(mixed $val): string
    {
        if (is_string($val)) {
            if (!is_numeric($val)) {
                throw new OrderValidationException("Invalid numerical value: {$val}");
            }
            return $val;
        }

        if (is_int($val) || is_float($val)) {
            return (string)$val;
        }

        throw new OrderValidationException("Unexpected numerical value type: " . get_debug_type($val));
    }

    public static function normalizeSymbol(string $symbol): string
    {
        return SymbolNormalizer::normalize($symbol);
    }

    /**
     * Builds a payload for a Market Order.
     *
     * @param string $symbol Trading symbol (e.g., 'BTC-EUR').
     * @param string $side Order side ('buy' or 'sell').
     * @param mixed $baseSize Amount in base currency.
     * @param mixed $quoteSize Amount in quote currency.
     * @param string|null $clientOrderId Unique client order ID (UUID generated if null).
     * @return array<string, mixed>
     *
     * @throws OrderValidationException
     */
    public static function buildMarketOrder(
        string $symbol,
        string $side,
        mixed $baseSize = null,
        mixed $quoteSize = null,
        ?string $clientOrderId = null
    ): array {
        if (($baseSize === null && $quoteSize === null) || ($baseSize !== null && $quoteSize !== null)) {
            throw new OrderValidationException("You must specify exactly one field: either 'base_size' or 'quote_size'.");
        }

        $marketConf = [];
        if ($baseSize !== null) {
            $marketConf['base_size'] = self::formatDecimal($baseSize);
        } else {
            $marketConf['quote_size'] = self::formatDecimal($quoteSize);
        }

        return [
            'client_order_id' => $clientOrderId ?? self::uuid4(),
            'symbol' => self::normalizeSymbol($symbol),
            'side' => strtolower($side),
            'order_configuration' => [
                'market' => $marketConf,
            ],
        ];
    }

    /**
     * Builds a payload for a Limit Order.
     *
     * @param string $symbol Trading symbol (e.g., 'BTC-EUR').
     * @param string $side Order side ('buy' or 'sell').
     * @param mixed $price Limit price in quote currency.
     * @param mixed $baseSize Amount in base currency.
     * @param mixed $quoteSize Amount in quote currency.
     * @param bool $postOnly Ensure order enters as Maker (0.00% fee).
     * @param string $timeInForce Time in force policy (default: 'gtc').
     * @param string|null $clientOrderId Unique client order ID.
     * @return array<string, mixed>
     *
     * @throws OrderValidationException
     */
    public static function buildLimitOrder(
        string $symbol,
        string $side,
        mixed $price,
        mixed $baseSize = null,
        mixed $quoteSize = null,
        bool $postOnly = false,
        string $timeInForce = TimeInForce::GTC,
        ?string $clientOrderId = null
    ): array {
        if (($baseSize === null && $quoteSize === null) || ($baseSize !== null && $quoteSize !== null)) {
            throw new OrderValidationException("You must specify exactly one field: either 'base_size' or 'quote_size'.");
        }

        $executionInstructions = $postOnly ? ['post_only'] : ['allow_taker'];

        $limitConf = [
            'price' => self::formatDecimal($price),
            'time_in_force' => strtolower($timeInForce),
            'execution_instructions' => $executionInstructions,
        ];

        if ($baseSize !== null) {
            $limitConf['base_size'] = self::formatDecimal($baseSize);
        } else {
            $limitConf['quote_size'] = self::formatDecimal($quoteSize);
        }

        return [
            'client_order_id' => $clientOrderId ?? self::uuid4(),
            'symbol' => self::normalizeSymbol($symbol),
            'side' => strtolower($side),
            'order_configuration' => [
                'limit' => $limitConf,
            ],
        ];
    }

    /**
     * Builds a payload for either a Market or Limit Order based on orderType.
     *
     * @return array<string, mixed>
     * @throws OrderValidationException
     */
    public static function buildOrder(
        string $symbol,
        string $side,
        string $orderType = OrderType::MARKET,
        mixed $price = null,
        mixed $baseSize = null,
        mixed $quoteSize = null,
        bool $postOnly = false,
        string $timeInForce = TimeInForce::GTC,
        ?string $clientOrderId = null
    ): array {
        $orderType = strtolower($orderType);
        $side = strtolower($side);

        if (!OrderType::isValid($orderType)) {
            throw new OrderValidationException("Invalid order_type: '{$orderType}'. Expected 'market' or 'limit'.");
        }

        if (!OrderSide::isValid($side)) {
            throw new OrderValidationException("Invalid side: '{$side}'. Expected 'buy' or 'sell'.");
        }

        if ($orderType === OrderType::MARKET) {
            if ($price !== null) {
                throw new OrderValidationException("Parameter 'price' is not supported for market orders.");
            }
            if ($postOnly) {
                throw new OrderValidationException("Parameter 'post_only' is not supported for market orders.");
            }
            return self::buildMarketOrder(
                symbol: $symbol,
                side: $side,
                baseSize: $baseSize,
                quoteSize: $quoteSize,
                clientOrderId: $clientOrderId
            );
        }

        if ($price === null) {
            throw new OrderValidationException("Parameter 'price' is required for limit orders.");
        }

        return self::buildLimitOrder(
            symbol: $symbol,
            side: $side,
            price: $price,
            baseSize: $baseSize,
            quoteSize: $quoteSize,
            postOnly: $postOnly,
            timeInForce: $timeInForce,
            clientOrderId: $clientOrderId
        );
    }

    /**
     * Builds a payload for a guaranteed zero-fee Maker Order (Limit with post_only=true).
     *
     * @return array<string, mixed>
     */
    public static function buildMakerOrder(
        string $symbol,
        string $side,
        mixed $price,
        mixed $baseSize = null,
        mixed $quoteSize = null,
        string $timeInForce = TimeInForce::GTC,
        ?string $clientOrderId = null
    ): array {
        return self::buildLimitOrder(
            symbol: $symbol,
            side: $side,
            price: $price,
            baseSize: $baseSize,
            quoteSize: $quoteSize,
            postOnly: true,
            timeInForce: $timeInForce,
            clientOrderId: $clientOrderId
        );
    }

    /**
     * Validates the constructed payload against the exchange's trading pair rules.
     *
     * @param array<string, mixed> $payload
     * @param array<string, mixed> $pairRules
     * @return array{0: bool, 1: list<string>} [isValid, errors]
     */
    public static function validateAgainstPairRules(array $payload, array $pairRules): array
    {
        $errors = [];
        $conf = $payload['order_configuration'] ?? [];

        $isMarket = isset($conf['market']);
        $isLimit = isset($conf['limit']);
        $orderData = $isMarket ? ($conf['market'] ?? []) : ($conf['limit'] ?? []);

        $baseSize = $orderData['base_size'] ?? null;
        $quoteSize = $orderData['quote_size'] ?? null;
        $price = $orderData['price'] ?? null;

        $minBase = (float)($pairRules['min_order_size'] ?? 0.00000001);
        $maxBase = (float)($pairRules['max_order_size'] ?? 1000000);
        $minQuote = (float)($pairRules['min_order_size_quote'] ?? 0.1);
        $maxQuote = (float)($pairRules['max_order_size_quote'] ?? 1000000);

        if ($baseSize !== null) {
            $b = (float)$baseSize;
            if ($b < $minBase) {
                $errors[] = "base_size ({$b}) is less than the minimum ({$minBase})";
            }
            if ($b > $maxBase) {
                $errors[] = "base_size ({$b}) is greater than the maximum ({$maxBase})";
            }
        }

        if ($quoteSize !== null) {
            $q = (float)$quoteSize;
            if ($q < $minQuote) {
                $errors[] = "quote_size ({$q}) is less than the minimum ({$minQuote})";
            }
            if ($q > $maxQuote) {
                $errors[] = "quote_size ({$q}) is greater than the maximum ({$maxQuote})";
            }
        }

        if ($isLimit && ($price === null || $price === '')) {
            $errors[] = "Limit order is missing the 'price' field!";
        }

        return [empty($errors), $errors];
    }
}
