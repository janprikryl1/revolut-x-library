<?php

declare(strict_types=1);

namespace RevolutX\Types;

/**
 * Candlestick interval in minutes for Revolut X OHLCV queries.
 */
final class Interval
{
    public const M1 = 1;
    public const M5 = 5;
    public const M15 = 15;
    public const H1 = 60;
    public const H4 = 240;
    public const D1 = 1440;

    // Verbose aliases
    public const MINUTE_1 = 1;
    public const MINUTE_5 = 5;
    public const MINUTE_15 = 15;
    public const HOUR_1 = 60;
    public const HOUR_4 = 240;
    public const DAY_1 = 1440;

    /**
     * @return array<int>
     */
    public static function all(): array
    {
        return [self::M1, self::M5, self::M15, self::H1, self::H4, self::D1];
    }

    public static function isValid(int $interval): bool
    {
        return in_array($interval, self::all(), true);
    }
}
