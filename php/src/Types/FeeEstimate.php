<?php

declare(strict_types=1);

namespace RevolutX\Types;

/**
 * Estimated fee calculation result for an order.
 */
final class FeeEstimate
{
    public function __construct(
        public string $side,
        public string $orderType,
        public bool $isMaker,
        public string $feeRatePercent,
        public string $tradeValueEur,
        public string $estimatedBaseQty,
        public string $price,
        public string $feeAmount,
        public string $feeCurrency,
        public string $netReceived,
        public string $netReceivedCurrency,
        public string $explanation
    ) {
    }

    /**
     * @return array<string, mixed>
     */
    public function toArray(): array
    {
        return [
            'side' => $this->side,
            'order_type' => $this->orderType,
            'is_maker' => $this->isMaker,
            'fee_rate_percent' => $this->feeRatePercent,
            'trade_value_eur' => $this->tradeValueEur,
            'estimated_base_qty' => $this->estimatedBaseQty,
            'price' => $this->price,
            'fee_amount' => $this->feeAmount,
            'fee_currency' => $this->feeCurrency,
            'net_received' => $this->netReceived,
            'net_received_currency' => $this->netReceivedCurrency,
            'explanation' => $this->explanation,
        ];
    }
}
