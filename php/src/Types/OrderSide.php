<?php

declare(strict_types=1);

namespace RevolutX\Types;

/**
 * Direction of an order on Revolut X.
 */
final class OrderSide
{
    public const BUY = 'buy';
    public const SELL = 'sell';

    /**
     * @return array<string>
     */
    public static function all(): array
    {
        return [self::BUY, self::SELL];
    }

    public static function isValid(string $side): bool
    {
        return in_array(strtolower($side), self::all(), true);
    }
}
