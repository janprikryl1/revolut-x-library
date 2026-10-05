<?php

declare(strict_types=1);

namespace RevolutX\Orders;

use InvalidArgumentException;
use RevolutX\Helpers\MakerOrderStrategy;
use RevolutX\Helpers\OrderPayloadBuilder;
use RevolutX\Types\OrderSide;
use RevolutX\Types\OrderType;
use RevolutX\Types\TimeInForce;

trait OrdersTrait
{
    /**
     * Submit an order to the exchange.
     *
     * @param string|array<string, mixed> $symbolOrPayload Trading symbol (e.g. 'BTC-EUR') or complete payload array.
     * @param string|null $side 'buy' or 'sell' (required if symbol string given).
     * @param string $orderType 'market' or 'limit'.
     * @param string|null $price Limit price in quote currency.
     * @param string|null $baseSize Amount in base currency.
     * @param string|null $quoteSize Amount in quote currency.
     * @param bool $postOnly If true, guarantees Maker order (0% fee).
     * @param string $timeInForce 'gtc' or 'ioc'.
     * @param string|null $clientOrderId UUID for idempotency.
     * @return array<string, mixed>
     */
    public function placeOrder(
        string|array $symbolOrPayload,
        ?string $side = null,
        string $orderType = OrderType::MARKET,
        ?string $price = null,
        ?string $baseSize = null,
        ?string $quoteSize = null,
        bool $postOnly = false,
        string $timeInForce = TimeInForce::GTC,
        ?string $clientOrderId = null
    ): array {
        if (is_array($symbolOrPayload)) {
            $payload = $symbolOrPayload;
        } else {
            if ($side === null) {
                throw new InvalidArgumentException("Parameter 'side' ('buy'/'sell') is required when placing an order by symbol.");
            }
            $payload = OrderPayloadBuilder::buildOrder(
                symbol: $symbolOrPayload,
                side: $side,
                orderType: $orderType,
                price: $price,
                baseSize: $baseSize,
                quoteSize: $quoteSize,
                postOnly: $postOnly,
                timeInForce: $timeInForce,
                clientOrderId: $clientOrderId
            );
        }

        $resp = $this->http->request('POST', '/orders', null, $payload, true);

        if (is_array($resp) && isset($resp['data'])) {
            $data = $resp['data'];
            if (is_array($data) && isset($data[0]) && is_array($data[0])) {
                return $data[0];
            }
            return is_array($data) ? $data : $resp;
        }

        return is_array($resp) ? $resp : [];
    }

    /**
     * Place a market order (immediate execution, 0.09% taker fee).
     * Exactly one of baseSize or quoteSize must be provided.
     *
     * @return array<string, mixed>
     */
    public function placeMarketOrder(
        string $symbol,
        string $side,
        ?string $baseSize = null,
        ?string $quoteSize = null,
        ?string $clientOrderId = null
    ): array {
        return $this->placeOrder(
            symbolOrPayload: $symbol,
            side: $side,
            orderType: OrderType::MARKET,
            baseSize: $baseSize,
            quoteSize: $quoteSize,
            clientOrderId: $clientOrderId
        );
    }

    /**
     * Place a limit order at a specific price.
     * Exactly one of baseSize or quoteSize must be provided.
     *
     * @return array<string, mixed>
     */
    public function placeLimitOrder(
        string $symbol,
        string $side,
        string $price,
        ?string $baseSize = null,
        ?string $quoteSize = null,
        bool $postOnly = false,
        string $timeInForce = TimeInForce::GTC,
        ?string $clientOrderId = null
    ): array {
        return $this->placeOrder(
            symbolOrPayload: $symbol,
            side: $side,
            orderType: OrderType::LIMIT,
            price: $price,
            baseSize: $baseSize,
            quoteSize: $quoteSize,
            postOnly: $postOnly,
            timeInForce: $timeInForce,
            clientOrderId: $clientOrderId
        );
    }

    /**
     * Fetches current ticker for symbol and calculates optimal Maker price.
     */
    public function calculateMakerPrice(
        string $symbol,
        string $side,
        mixed $offset = '0.10',
        mixed $tickSize = '0.01'
    ): string {
        $ticker = $this->getTicker($symbol);
        return MakerOrderStrategy::calculateMakerPrice(
            side: $side,
            bestBid: $ticker['bid'] ?? null,
            bestAsk: $ticker['ask'] ?? null,
            lastPrice: $ticker['last_price'] ?? null,
            offset: $offset,
            tickSize: $tickSize
        );
    }

    /**
     * Place a guaranteed zero-fee Maker limit order (0.00% fee).
     * If price is not provided, automatically calculates price from live order book.
     *
     * @return array<string, mixed>
     */
    public function placeMakerOrder(
        string $symbol,
        string $side,
        ?string $price = null,
        mixed $offset = '0.10',
        mixed $tickSize = '0.01',
        ?string $baseSize = null,
        ?string $quoteSize = null,
        string $timeInForce = TimeInForce::GTC,
        ?string $clientOrderId = null
    ): array {
        $calcPrice = $price ?? $this->calculateMakerPrice($symbol, $side, $offset, $tickSize);

        return $this->placeLimitOrder(
            symbol: $symbol,
            side: $side,
            price: $calcPrice,
            baseSize: $baseSize,
            quoteSize: $quoteSize,
            postOnly: true,
            timeInForce: $timeInForce,
            clientOrderId: $clientOrderId
        );
    }

    /**
     * Retrieve detailed information about a specific order.
     *
     * @return array<string, mixed>
     */
    public function getOrder(string $orderId): array
    {
        $resp = $this->http->request('GET', "/orders/{$orderId}", null, null, true);
        if (is_array($resp) && isset($resp['data']) && is_array($resp['data'])) {
            return $resp['data'];
        }
        return is_array($resp) ? $resp : [];
    }

    /**
     * Retrieve individual fills (executions) for an order.
     *
     * @return list<array<string, mixed>>
     */
    public function getOrderFills(string $orderId): array
    {
        $resp = $this->http->request('GET', "/orders/fills/{$orderId}", null, null, true);
        if (is_array($resp) && isset($resp['data']) && is_array($resp['data'])) {
            return $resp['data'];
        }
        return is_array($resp) ? $resp : [];
    }

    /**
     * Retrieve all currently open (active) orders.
     *
     * @return list<array<string, mixed>>
     */
    public function getActiveOrders(?string $symbol = null): array
    {
        $params = [];
        if ($symbol !== null) {
            $params['symbol'] = strtoupper(str_replace('/', '-', $symbol));
        }

        $resp = $this->http->request('GET', '/orders/active', $params, null, true);
        if (is_array($resp) && isset($resp['data']) && is_array($resp['data'])) {
            return $resp['data'];
        }
        return is_array($resp) ? $resp : [];
    }

    /**
     * Retrieve historical orders with cursor pagination.
     *
     * @return array{orders: list<array<string, mixed>>, next_cursor: string|null}
     */
    public function getHistoricalOrders(
        ?string $symbol = null,
        int $limit = 50,
        ?string $cursor = null
    ): array {
        $params = ['limit' => $limit];
        if ($symbol !== null) {
            $params['symbol'] = strtoupper(str_replace('/', '-', $symbol));
        }
        if ($cursor !== null) {
            $params['cursor'] = $cursor;
        }

        $resp = $this->http->request('GET', '/orders/historical', $params, null, true);
        $orders = [];
        $nextCursor = null;

        if (is_array($resp)) {
            $orders = isset($resp['data']) && is_array($resp['data']) ? $resp['data'] : [];
            $nextCursor = $resp['metadata']['next_cursor'] ?? null;
        }

        return [
            'orders' => $orders,
            'next_cursor' => $nextCursor,
        ];
    }

    /**
     * Cancel a specific open order.
     *
     * @return array<string, mixed>
     */
    public function cancelOrder(string $orderId): array
    {
        /** @var array<string, mixed> $resp */
        $resp = $this->http->request('DELETE', "/orders/{$orderId}", null, null, true);
        return is_array($resp) ? $resp : [];
    }

    /**
     * Cancel all open orders, optionally filtered by trading pair.
     *
     * @return array<string, mixed>
     */
    public function cancelAllOrders(?string $symbol = null): array
    {
        $params = [];
        if ($symbol !== null) {
            $params['symbol'] = strtoupper(str_replace('/', '-', $symbol));
        }

        /** @var array<string, mixed> $resp */
        $resp = $this->http->request('DELETE', '/orders', $params, null, true);
        return is_array($resp) ? $resp : [];
    }
}
