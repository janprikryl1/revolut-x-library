<?php

declare(strict_types=1);

namespace RevolutX\Http;

use RevolutX\Auth\Signer;
use RevolutX\Exceptions\ApiException;
use RevolutX\Exceptions\AuthenticationException;
use RevolutX\Exceptions\NetworkException;
use RevolutX\Exceptions\RateLimitException;

/**
 * Robust HTTP client using native cURL with automated rate limiting,
 * request signing, retry logic, and error handling for Revolut X.
 */
class HttpClient
{
    private string $baseUrl;
    private string $apiVersion;
    private ?string $apiKey;
    private ?string $secretKey;
    private float $requestDelay;
    private int $timeout;
    private int $maxRetries;
    private float $lastRequestTime = 0.0;

    public function __construct(
        string $baseUrl = 'https://revx.revolut.com/api',
        string $apiVersion = '1.0',
        ?string $apiKey = null,
        ?string $secretKey = null,
        float $requestDelay = 0.85,
        int $timeout = 15,
        int $maxRetries = 3
    ) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->apiVersion = trim($apiVersion, '/');
        $this->apiKey = $apiKey;
        $this->secretKey = $secretKey;
        $this->requestDelay = $requestDelay;
        $this->timeout = $timeout;
        $this->maxRetries = $maxRetries;
    }

    public function isAuthenticated(): bool
    {
        return $this->apiKey !== null && $this->secretKey !== null;
    }

    /**
     * Executes an HTTP request with automatic signing, rate limiting, and retries.
     *
     * @param string $method HTTP method (GET, POST, DELETE, etc.).
     * @param string $path Endpoint path (e.g. '/orders' or '/public/tickers').
     * @param array<string, mixed>|null $params Query parameters.
     * @param mixed $body Request body (null, array, or object).
     * @param bool $auth Whether request must be authenticated.
     * @return mixed Parsed JSON response.
     *
     * @throws AuthenticationException
     * @throws RateLimitException
     * @throws ApiException
     * @throws NetworkException
     */
    public function request(
        string $method,
        string $path,
        ?array $params = null,
        mixed $body = null,
        bool $auth = false
    ): mixed {
        $method = strtoupper($method);

        // Normalize endpoint with api version
        $endpoint = str_starts_with($path, '/') ? $path : '/' . $path;

        if (str_starts_with($endpoint, "/api/{$this->apiVersion}")) {
            $apiPath = $endpoint;
            $urlPath = substr($endpoint, 4);
        } elseif (str_starts_with($endpoint, "/{$this->apiVersion}")) {
            $apiPath = '/api' . $endpoint;
            $urlPath = $endpoint;
        } else {
            $apiPath = "/api/{$this->apiVersion}" . $endpoint;
            $urlPath = "/{$this->apiVersion}" . $endpoint;
        }

        // Build URL
        $url = $this->baseUrl . $urlPath;
        if ($params !== null && !empty($params)) {
            $filtered = [];
            foreach ($params as $k => $v) {
                if ($v !== null) {
                    $filtered[(string)$k] = (string)$v;
                }
            }
            if (!empty($filtered)) {
                $url .= '?' . http_build_query($filtered, '', '&', PHP_QUERY_RFC3986);
            }
        }

        $headers = [
            'User-Agent: revolut-x-php/0.1.0',
            'Accept: application/json',
        ];

        if ($auth) {
            if (!$this->isAuthenticated()) {
                throw new AuthenticationException(
                    "Endpoint {$method} {$path} requires authentication, but apiKey or privateKey is missing.",
                    "Provide apiKey and privateKey when instantiating RevolutXClient."
                );
            }

            $authHeaders = Signer::signRequest(
                apiKey: $this->apiKey,
                secretKey: $this->secretKey,
                method: $method,
                path: $apiPath,
                params: $params,
                body: $body
            );

            foreach ($authHeaders as $headerKey => $headerVal) {
                $headers[] = "{$headerKey}: {$headerVal}";
            }
        } elseif ($body !== null) {
            $headers[] = 'Content-Type: application/json';
        }

        $postData = null;
        if ($body !== null) {
            $postData = is_string($body) ? $body : json_encode($body, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        }

        $attempt = 0;
        while (true) {
            $attempt++;

            // Rate limiting delay
            $this->enforceRateLimit();

            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
            curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_HEADER, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

            if ($postData !== null) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
            }

            $rawResult = curl_exec($ch);
            $curlError = curl_error($ch);
            $curlErrno = curl_errno($ch);
            $headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
            $httpCode = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
            unset($ch);

            $this->lastRequestTime = microtime(true);

            if ($rawResult === false || $curlErrno !== 0) {
                if ($attempt <= $this->maxRetries) {
                    usleep(500000 * $attempt); // 0.5s, 1.0s, 1.5s
                    continue;
                }
                throw new NetworkException("cURL error ({$curlErrno}): {$curlError}");
            }

            $rawHeaders = substr((string)$rawResult, 0, $headerSize);
            $rawBody = substr((string)$rawResult, $headerSize);

            // Handle 429 Too Many Requests
            if ($httpCode === 429) {
                $retryAfter = $this->extractRetryAfter($rawHeaders) ?? 1;
                if ($attempt <= $this->maxRetries) {
                    sleep($retryAfter);
                    continue;
                }
                throw new RateLimitException(
                    "Rate limit exceeded after {$this->maxRetries} retries.",
                    $retryAfter
                );
            }

            // Handle 5xx server errors with retry
            if ($httpCode >= 500 && $attempt <= $this->maxRetries) {
                usleep(500000 * $attempt);
                continue;
            }

            // Parse response body
            $parsedBody = json_decode($rawBody, true);
            if ($parsedBody === null && json_last_error() !== JSON_ERROR_NONE && !empty($rawBody)) {
                $parsedBody = $rawBody;
            }

            // Check non-2xx codes
            if ($httpCode < 200 || $httpCode >= 300) {
                $this->handleHttpError($httpCode, $parsedBody);
            }

            return $parsedBody;
        }
    }

    private function enforceRateLimit(): void
    {
        if ($this->requestDelay > 0 && $this->lastRequestTime > 0) {
            $elapsed = microtime(true) - $this->lastRequestTime;
            if ($elapsed < $this->requestDelay) {
                $sleepUs = (int) (($this->requestDelay - $elapsed) * 1000000);
                if ($sleepUs > 0) {
                    usleep($sleepUs);
                }
            }
        }
    }

    private function extractRetryAfter(string $headers): ?int
    {
        if (preg_match('/^retry-after:\s*(\d+)/im', $headers, $matches)) {
            return (int) $matches[1];
        }
        return null;
    }

    /**
     * @throws AuthenticationException
     * @throws ApiException
     */
    private function handleHttpError(int $httpCode, mixed $body): never
    {
        $message = "Request failed with HTTP {$httpCode}";
        $errorCode = null;

        if (is_array($body)) {
            $message = $body['message'] ?? $body['error'] ?? $body['msg'] ?? $message;
            $errorCode = isset($body['code']) ? (string) $body['code'] : null;
        } elseif (is_string($body) && !empty($body)) {
            $message = $body;
        }

        if ($httpCode === 401 || $httpCode === 403) {
            throw new AuthenticationException(
                "Authentication rejected (HTTP {$httpCode}): {$message}",
                "Verify that your API key is active and your Ed25519 private key corresponds to the public key registered on Revolut X."
            );
        }

        throw new ApiException(
            message: (string)$message,
            statusCode: $httpCode,
            responseBody: $body,
            errorCode: $errorCode
        );
    }
}
