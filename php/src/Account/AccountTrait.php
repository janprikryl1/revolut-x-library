<?php

declare(strict_types=1);

namespace RevolutX\Account;

trait AccountTrait
{
    /**
     * Retrieve current balances for all currencies on the account.
     *
     * @return list<array<string, mixed>>
     */
    public function getBalances(): array
    {
        $resp = $this->http->request('GET', '/balances', null, null, true);
        return is_array($resp) ? $resp : [];
    }

    /**
     * Retrieve the balance for a specific currency.
     *
     * @param string $currency Currency symbol (e.g. 'EUR', 'BTC', 'ETH').
     * @return array<string, mixed>
     */
    public function getBalance(string $currency): array
    {
        $balances = $this->getBalances();
        $target = strtoupper($currency);

        foreach ($balances as $item) {
            if (is_array($item) && isset($item['currency']) && strtoupper((string)$item['currency']) === $target) {
                return $item;
            }
        }

        return [
            'currency' => $target,
            'available' => '0.00',
            'reserved' => '0.00',
            'total' => '0.00',
        ];
    }

    /**
     * Retrieve account transaction history (ledger).
     *
     * @return array{transactions: list<array<string, mixed>>, next_cursor: string|null}
     */
    public function getTransactions(int $limit = 50, ?string $cursor = null): array
    {
        $params = ['limit' => $limit];
        if ($cursor !== null) {
            $params['cursor'] = $cursor;
        }

        $resp = $this->http->request('GET', '/transactions', $params, null, true);
        $transactions = [];
        $nextCursor = null;

        if (is_array($resp)) {
            $transactions = isset($resp['data']) && is_array($resp['data']) ? $resp['data'] : [];
            $nextCursor = $resp['metadata']['next_cursor'] ?? null;
        }

        return [
            'transactions' => $transactions,
            'next_cursor' => $nextCursor,
        ];
    }

    /**
     * Retrieve private (your own) trade history for a trading pair.
     *
     * @param string $symbol Trading pair (e.g. 'BTC-EUR').
     * @return array{trades: list<array<string, mixed>>, next_cursor: string|null}
     */
    public function getAccountTrades(
        string $symbol,
        int $limit = 50,
        ?string $cursor = null
    ): array {
        $apiSymbol = strtoupper(str_replace('/', '-', $symbol));
        $params = ['limit' => $limit];
        if ($cursor !== null) {
            $params['cursor'] = $cursor;
        }

        $resp = $this->http->request('GET', "/trades/private/{$apiSymbol}", $params, null, true);
        $trades = [];
        $nextCursor = null;

        if (is_array($resp)) {
            $trades = isset($resp['data']) && is_array($resp['data']) ? $resp['data'] : [];
            $nextCursor = $resp['metadata']['next_cursor'] ?? null;
        }

        return [
            'trades' => $trades,
            'next_cursor' => $nextCursor,
        ];
    }
}
