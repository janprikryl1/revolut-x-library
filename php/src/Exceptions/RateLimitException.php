<?php

declare(strict_types=1);

namespace RevolutX\Exceptions;

use Throwable;

/**
 * Raised when the Revolut X API returns HTTP 429 (Too Many Requests).
 */
class RateLimitException extends RevolutXException
{
    protected ?int $retryAfterSeconds;

    public function __construct(string $message = "", ?int $retryAfterSeconds = null, int $code = 429, ?Throwable $previous = null)
    {
        $this->retryAfterSeconds = $retryAfterSeconds;
        $fullMessage = $retryAfterSeconds !== null
            ? "{$message} (retry after {$retryAfterSeconds}s)"
            : $message;
        parent::__construct($fullMessage, $code, $previous);
    }

    public function getRetryAfterSeconds(): ?int
    {
        return $this->retryAfterSeconds;
    }
}
