<?php

declare(strict_types=1);

namespace RevolutX\Market;

use InvalidArgumentException;
use RevolutX\Helpers\SymbolNormalizer;
use RevolutX\Types\Interval;

trait MarketTrait
{
    /**
     * Retrieve the configuration and trading limits for all active pairs.
     *
     * @return array<string, mixed>
     */
    public function getPairs(): array
    {
        /** @var array<string, mixed> $data */
        $data = $this->http->request('GET', '/public/configuration/pairs');
        return $data;
    }

    /**
     * Retrieve the configuration for a specific trading pair.
     *
     * @param string $symbol Trading pair (e.g. 'BTC-EUR', 'BTC/EUR', 'btceur').
     * @return array<string, mixed>
     *
     * @throws InvalidArgumentException
     */
    public function getPair(string $symbol): array
    {
        $pairs = $this->getPairs();

        $cleanSlash = strtoupper(str_replace('-', '/', $symbol));
        $cleanDash = strtoupper(str_replace('/', '-', $symbol));

        if (isset($pairs[$cleanSlash])) {
            return $pairs[$cleanSlash];
        }
        if (isset($pairs[$cleanDash])) {
            return $pairs[$cleanDash];
        }

        foreach ($pairs as $k => $v) {
            $upperK = strtoupper((string)$k);
            if ($upperK === $cleanSlash || $upperK === $cleanDash) {
                return $v;
            }
        }

        $available = implode(', ', array_slice(array_keys($pairs), 0, 10));
        throw new InvalidArgumentException(
            "Trading pair '{$symbol}' not found on Revolut X. Available pairs include: {$available}..."
        );
    }

    /**
     * Retrieve the configuration for all supported currencies.
     *
     * @return array<string, mixed>
     */
    public function getCurrencies(): array
    {
        /** @var array<string, mixed> $data */
        $data = $this->http->request('GET', '/public/configuration/currencies');
        return $data;
    }

    /**
     * Retrieve current tickers (best bid, best ask, last price) for all pairs.
     *
     * @return list<array<string, mixed>>
     */
    public function getTickers(): array
    {
        $data = $this->http->request('GET', '/public/tickers');
        if (is_array($data) && isset($data['data']) && is_array($data['data'])) {
            return $data['data'];
        }
        return is_array($data) ? $data : [];
    }

    /**
     * Retrieve the current ticker for a specific trading pair.
     *
     * @param string $symbol Trading pair (e.g. 'BTC-EUR').
     * @return array<string, mixed>
     *
     * @throws InvalidArgumentException
     */
    public function getTicker(string $symbol): array
    {
        $tickers = $this->getTickers();

        $targetSlash = strtoupper(str_replace('-', '/', $symbol));
        $targetDash = strtoupper(str_replace('/', '-', $symbol));

        foreach ($tickers as $t) {
            if (is_array($t) && isset($t['symbol'])) {
                $sym = strtoupper((string)$t['symbol']);
                if ($sym === $targetSlash || $sym === $targetDash) {
                    return $t;
                }
            }
        }

        throw new InvalidArgumentException(
            "Ticker data not available for '{$symbol}'. Check that the pair exists with getPairs()."
        );
    }

    /**
     * Retrieve the current order book (bids and asks) for a trading pair.
     *
     * @param string $symbol Trading pair (e.g. 'BTC-EUR').
     * @param int $depth Number of price levels (default: 10).
     * @return array<string, mixed>
     */
    public function getOrderBook(string $symbol, int $depth = 10): array
    {
        $apiSymbol = SymbolNormalizer::normalize($symbol);
        $data = $this->http->request('GET', "/public/order-book/{$apiSymbol}", ['limit' => $depth]);
        if (is_array($data) && isset($data['data']) && is_array($data['data'])) {
            return $data['data'];
        }
        return is_array($data) ? $data : [];
    }

    /**
     * Fetch up to 1000 OHLCV candlesticks for a trading pair.
     *
     * @param string $symbol Trading pair (e.g. 'BTC-EUR').
     * @param int $interval Interval in minutes (default: 60).
     * @param int|null $since Start time as Unix timestamp in milliseconds.
     * @param int|null $until End time as Unix timestamp in milliseconds.
     * @return list<array<string, mixed>>
     */
    public function getCandles(
        string $symbol,
        int $interval = Interval::H1,
        ?int $since = null,
        ?int $until = null
    ): array {
        $apiSymbol = SymbolNormalizer::normalize($symbol);
        $params = ['interval' => $interval];
        if ($since !== null) {
            $params['since'] = $since;
        }
        if ($until !== null) {
            $params['until'] = $until;
        }

        $data = $this->http->request('GET', "/public/candles/{$apiSymbol}", $params);
        if (is_array($data) && isset($data['data']) && is_array($data['data'])) {
            return $data['data'];
        }
        return is_array($data) ? $data : [];
    }

    /**
     * Fetch the most recent public trades for a trading pair.
     *
     * @param string $symbol Trading pair (e.g. 'BTC-EUR').
     * @param int $limit Number of trades (default: 100).
     * @param string|null $before Cursor to paginate backward.
     * @param string|null $after Cursor to paginate forward.
     * @return list<array<string, mixed>>
     */
    public function getTrades(
        string $symbol,
        int $limit = 100,
        ?string $before = null,
        ?string $after = null
    ): array {
        $apiSymbol = SymbolNormalizer::normalize($symbol);
        $params = ['limit' => $limit];
        if ($before !== null) {
            $params['before'] = $before;
        }
        if ($after !== null) {
            $params['after'] = $after;
        }

        $data = $this->http->request('GET', "/public/trades/{$apiSymbol}", $params);
        if (is_array($data) && isset($data['data']) && is_array($data['data'])) {
            return $data['data'];
        }
        return is_array($data) ? $data : [];
    }
}
