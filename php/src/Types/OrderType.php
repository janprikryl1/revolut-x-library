<?php

declare(strict_types=1);

namespace RevolutX\Types;

/**
 * Type of an order on Revolut X.
 */
final class OrderType
{
    public const MARKET = 'market';
    public const LIMIT = 'limit';

    /**
     * @return array<string>
     */
    public static function all(): array
    {
        return [self::MARKET, self::LIMIT];
    }

    public static function isValid(string $type): bool
    {
        return in_array(strtolower($type), self::all(), true);
    }
}
