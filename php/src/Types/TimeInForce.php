<?php

declare(strict_types=1);

namespace RevolutX\Types;

/**
 * Time-in-force policies supported by Revolut X.
 */
final class TimeInForce
{
    /** Good 'til Cancelled (default for limit orders). */
    public const GTC = 'gtc';

    /** Immediate or Cancel. */
    public const IOC = 'ioc';

    /** Fill or Kill. */
    public const FOK = 'fok';

    /**
     * @return array<string>
     */
    public static function all(): array
    {
        return [self::GTC, self::IOC, self::FOK];
    }

    public static function isValid(string $tif): bool
    {
        return in_array(strtolower($tif), self::all(), true);
    }
}
