<?php

declare(strict_types=1);

namespace RevolutX\Exceptions;

use Throwable;

/**
 * Raised when the Revolut X API returns a non-2xx HTTP response (other than 429).
 */
class ApiException extends RevolutXException
{
    protected int $statusCode;
    protected mixed $responseBody;
    protected ?string $errorCode;

    public function __construct(
        string $message,
        int $statusCode = 0,
        mixed $responseBody = null,
        ?string $errorCode = null,
        ?Throwable $previous = null
    ) {
        $this->statusCode = $statusCode;
        $this->responseBody = $responseBody;
        $this->errorCode = $errorCode;

        $msg = "HTTP {$statusCode}: {$message}";
        if ($errorCode !== null) {
            $msg .= " [code: {$errorCode}]";
        }

        parent::__construct($msg, $statusCode, $previous);
    }

    public function getStatusCode(): int
    {
        return $this->statusCode;
    }

    public function getResponseBody(): mixed
    {
        return $this->responseBody;
    }

    public function getErrorCode(): ?string
    {
        return $this->errorCode;
    }
}
