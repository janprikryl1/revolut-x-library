<?php

declare(strict_types=1);

namespace RevolutX\Helpers;

use RevolutX\Exceptions\OrderValidationException;
use RevolutX\Types\OrderSide;

/**
 * Calculates optimal prices for guaranteed 0% fee Maker limit orders.
 */
class MakerOrderStrategy
{
    /**
     * Calculates an optimal limit price to guarantee entry into the order book as a Maker (0.00% fee).
     *
     * For BUY orders:  price = (best_bid or last_price) - offset
     * For SELL orders: price = (best_ask or last_price) + offset
     *
     * @param string $side 'buy' or 'sell'.
     * @param mixed $bestBid Current best bid price (highest buyer in book).
     * @param mixed $bestAsk Current best ask price (lowest seller in book).
     * @param mixed $lastPrice Fallback price if best bid/ask is not available.
     * @param mixed $offset Safety offset in quote currency (default: 0.10).
     * @param mixed $tickSize Minimum price increment for quantisation (default: 0.01).
     * @return string The quantised target price as a decimal string.
     *
     * @throws OrderValidationException
     */
    public static function calculateMakerPrice(
        string $side,
        mixed $bestBid = null,
        mixed $bestAsk = null,
        mixed $lastPrice = null,
        mixed $offset = '0.10',
        mixed $tickSize = '0.01'
    ): string {
        $side = strtolower($side);
        if (!OrderSide::isValid($side)) {
            throw new OrderValidationException("Invalid side: '{$side}'. Expected 'buy' or 'sell'.");
        }

        $offsetFloat = (float)$offset;
        $tickFloat = (float)$tickSize;

        if ($side === OrderSide::BUY) {
            $ref = $bestBid ?? $lastPrice;
            if ($ref === null) {
                throw new OrderValidationException("Cannot calculate Maker BUY price: neither 'best_bid' nor 'last_price' provided.");
            }
            $rawPrice = (float)$ref - $offsetFloat;
        } else {
            $ref = $bestAsk ?? $lastPrice;
            if ($ref === null) {
                throw new OrderValidationException("Cannot calculate Maker SELL price: neither 'best_ask' nor 'last_price' provided.");
            }
            $rawPrice = (float)$ref + $offsetFloat;
        }

        $rounded = round($rawPrice / $tickFloat) * $tickFloat;
        $tickStr = (string)$tickSize;
        $dotPos = strpos($tickStr, '.');
        $precision = $dotPos !== false ? strlen(substr($tickStr, $dotPos + 1)) : 2;

        return number_format($rounded, $precision, '.', '');
    }
}
