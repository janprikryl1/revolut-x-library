<?php

declare(strict_types=1);

namespace RevolutX\Helpers;

use RevolutX\Exceptions\OrderValidationException;
use RevolutX\Types\FeeEstimate;
use RevolutX\Types\OrderSide;

/**
 * Calculator for order fees on Revolut X.
 */
class FeeCalculator
{
    public const MAKER_FEE_RATE = 0.0000; // 0.00%
    public const TAKER_FEE_RATE = 0.0009; // 0.09%

    /**
     * Calculates exact fees and net received amount for a specified trade.
     *
     * @param string $side 'buy' or 'sell'.
     * @param mixed $price Execution price in quote currency.
     * @param bool $isMaker True if maker (0.00%), false if taker (0.09%).
     * @param mixed $baseSize Amount in base currency.
     * @param mixed $quoteSize Amount in quote currency.
     * @return FeeEstimate
     *
     * @throws OrderValidationException
     */
    public static function calculate(
        string $side,
        mixed $price,
        bool $isMaker,
        mixed $baseSize = null,
        mixed $quoteSize = null
    ): FeeEstimate {
        $side = strtolower($side);
        if (!OrderSide::isValid($side)) {
            throw new OrderValidationException("Invalid side: '{$side}'. Expected 'buy' or 'sell'.");
        }

        $priceFloat = (float)$price;
        if ($priceFloat <= 0) {
            throw new OrderValidationException("Price must be greater than zero.");
        }

        $rate = $isMaker ? self::MAKER_FEE_RATE : self::TAKER_FEE_RATE;
        $ratePct = $rate * 100.0;

        if ($quoteSize !== null) {
            $valueEur = (float)$quoteSize;
            $qtyBtc = round($valueEur / $priceFloat, 8);
        } elseif ($baseSize !== null) {
            $qtyBtc = (float)$baseSize;
            $valueEur = round($qtyBtc * $priceFloat, 2);
        } else {
            throw new OrderValidationException("You must specify either 'base_size' or 'quote_size'.");
        }

        $feeEur = round($valueEur * $rate, 4);

        if ($side === OrderSide::BUY) {
            $feeCurrency = 'EUR';
            $netReceived = $qtyBtc;
            $netCurrency = 'BTC';
            $explanation = sprintf(
                "Buy %s BTC for %s EUR at price %s.\n- Execution type: %s\n- Fee rate: %.2f %%\n- Fee amount: %.4f EUR\n- Net received approx: %.8f BTC",
                number_format($netReceived, 8, '.', ''),
                number_format($valueEur, 2, '.', ''),
                (string)$price,
                $isMaker ? 'MAKER' : 'TAKER',
                $ratePct,
                $feeEur,
                $netReceived
            );
        } else {
            $feeCurrency = 'EUR';
            $netReceivedVal = round($valueEur - $feeEur, 2);
            $netReceived = number_format($netReceivedVal, 2, '.', '');
            $netCurrency = 'EUR';
            $explanation = sprintf(
                "Sell %s BTC at price %s (Gross value: %s EUR).\n- Execution type: %s\n- Fee rate: %.2f %%\n- Fee amount: %.4f EUR\n- Net received: %s EUR",
                number_format($qtyBtc, 8, '.', ''),
                (string)$price,
                number_format($valueEur, 2, '.', ''),
                $isMaker ? 'MAKER' : 'TAKER',
                $ratePct,
                $feeEur,
                $netReceived
            );
        }

        return new FeeEstimate(
            side: $side,
            orderType: $isMaker ? 'limit' : 'market/immediate-limit',
            isMaker: $isMaker,
            feeRatePercent: number_format($ratePct, 2, '.', ''),
            tradeValueEur: number_format($valueEur, 2, '.', ''),
            estimatedBaseQty: number_format($qtyBtc, 8, '.', ''),
            price: (string)$price,
            feeAmount: number_format($feeEur, 4, '.', ''),
            feeCurrency: $feeCurrency,
            netReceived: (string)$netReceived,
            netReceivedCurrency: $netCurrency,
            explanation: $explanation
        );
    }
}
