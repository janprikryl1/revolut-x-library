<?php

declare(strict_types=1);

namespace RevolutX;

use RevolutX\Account\AccountTrait;
use RevolutX\Auth\Signer;
use RevolutX\Http\HttpClient;
use RevolutX\Market\MarketTrait;
use RevolutX\Orders\OrdersTrait;

/**
 * Main client for the Revolut X Crypto Exchange REST API.
 * Combines public market data, order execution, and account management.
 */
class Client
{
    use MarketTrait;
    use OrdersTrait;
    use AccountTrait;

    protected HttpClient $http;

    /**
     * @param string|null $apiKey Revolut X API key (required for orders, balances).
     * @param string|null $privateKeyPath Path to Ed25519 private key PEM file.
     * @param string|null $privateKeyBytes Raw PEM string or raw Ed25519 key bytes.
     * @param string $baseUrl API base URL (default: 'https://revx.revolut.com/api').
     * @param string $apiVersion API version (default: '1.0').
     * @param float $requestDelay Minimum delay between HTTP requests in seconds (default: 0.85).
     * @param int $timeout cURL request timeout in seconds (default: 15).
     * @param int $maxRetries Maximum retry attempts on 429/5xx (default: 3).
     */
    public function __construct(
        ?string $apiKey = null,
        ?string $privateKeyPath = null,
        ?string $privateKeyBytes = null,
        string $baseUrl = 'https://revx.revolut.com/api',
        string $apiVersion = '1.0',
        float $requestDelay = 0.85,
        int $timeout = 15,
        int $maxRetries = 3
    ) {
        $secretKey = null;

        if ($privateKeyPath !== null) {
            $secretKey = Signer::loadPrivateKey($privateKeyPath);
        } elseif ($privateKeyBytes !== null) {
            $secretKey = Signer::loadPrivateKey($privateKeyBytes);
        }

        $this->http = new HttpClient(
            baseUrl: $baseUrl,
            apiVersion: $apiVersion,
            apiKey: $apiKey,
            secretKey: $secretKey,
            requestDelay: $requestDelay,
            timeout: $timeout,
            maxRetries: $maxRetries
        );
    }

    public function isAuthenticated(): bool
    {
        return $this->http->isAuthenticated();
    }

    public function getHttpClient(): HttpClient
    {
        return $this->http;
    }
}
