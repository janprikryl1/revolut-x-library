<?php

declare(strict_types=1);

namespace RevolutX\Helpers;

/**
 * Normalizes trading symbol strings for the Revolut X API.
 */
class SymbolNormalizer
{
    /**
     * Normalizes the trading symbol for the Revolut X API.
     * Accepts formats such as 'BTC/EUR', 'BTC-EUR', 'btc-eur', 'btceur', 'BTCEUR'.
     * Returns the normalized symbol with a dash separator (e.g. 'BTC-EUR').
     */
    public static function normalize(string $symbol): string
    {
        $clean = strtoupper(str_replace(['/', '-'], '', $symbol));

        foreach (['USDC', 'EUR', 'USD', 'GBP', 'CZK'] as $quote) {
            if (str_ends_with($clean, $quote)) {
                $base = substr($clean, 0, -strlen($quote));
                if ($base !== '') {
                    return "{$base}-{$quote}";
                }
            }
        }

        return strtoupper(str_replace('/', '-', $symbol));
    }
}
