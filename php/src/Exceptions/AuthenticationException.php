<?php

declare(strict_types=1);

namespace RevolutX\Exceptions;

use Throwable;

/**
 * Raised when authentication is missing, misconfigured, or rejected.
 */
class AuthenticationException extends RevolutXException
{
    protected ?string $hint;

    public function __construct(string $message = "", ?string $hint = null, int $code = 0, ?Throwable $previous = null)
    {
        $this->hint = $hint;
        $fullMessage = $hint !== null ? "{$message}\n  Hint: {$hint}" : $message;
        parent::__construct($fullMessage, $code, $previous);
    }

    public function getHint(): ?string
    {
        return $this->hint;
    }
}
