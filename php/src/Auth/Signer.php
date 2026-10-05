<?php

declare(strict_types=1);

namespace RevolutX\Auth;

use RevolutX\Exceptions\AuthenticationException;
use Throwable;

/**
 * Handles Ed25519 cryptographic signing for Revolut X REST API requests.
 */
class Signer
{
    /**
     * ASN.1 OID for Ed25519 (1.3.101.112): 06 03 2B 65 70
     */
    private const ED25519_OID_HEX = '06032b6570';

    /**
     * Standard PKCS#8 v1 prefix for Ed25519 private key: 302e020100300506032b657004220420
     */
    private const ED25519_PKCS8_PREFIX_HEX = '302e020100300506032b657004220420';

    /**
     * Loads an Ed25519 private key from a file path or raw string/PEM.
     * Returns a 64-byte sodium secret key string ready for sodium_crypto_sign_detached.
     *
     * @param string $source File path or raw PEM content / raw key bytes.
     * @return string 64-byte sodium secret key (seed + public key).
     * @throws AuthenticationException
     */
    public static function loadPrivateKey(string $source): string
    {
        $raw = $source;

        // 1. If it's already a 64-byte raw secret key
        if (strlen($source) === SODIUM_CRYPTO_SIGN_SECRETKEYBYTES && !str_contains($source, '-----BEGIN')) {
            return $source;
        }

        // 2. If it's a 32-byte raw seed
        if (strlen($source) === SODIUM_CRYPTO_SIGN_SEEDBYTES && !str_contains($source, '-----BEGIN')) {
            $keypair = sodium_crypto_sign_seed_keypair($source);
            return sodium_crypto_sign_secretkey($keypair);
        }

        // 3. Check if $source is a file path (ends with .pem / .key or file actually exists)
        if (!str_contains($source, "\n") && (is_file($source) || str_ends_with($source, '.pem') || str_ends_with($source, '.key'))) {
            if (!file_exists($source) || !is_file($source)) {
                throw new AuthenticationException("Private key file not found at: {$source}");
            }
            $content = file_get_contents($source);
            if ($content === false) {
                throw new AuthenticationException("Failed to read private key file at {$source}");
            }
            $raw = $content;
        }

        // 4. Parse PEM format if PEM headers are present
        if (str_contains($raw, '-----BEGIN')) {
            return self::parsePem($raw);
        }

        // 5. If content read from file was 64-byte or 32-byte raw key
        if (strlen($raw) === SODIUM_CRYPTO_SIGN_SECRETKEYBYTES) {
            return $raw;
        }
        if (strlen($raw) === SODIUM_CRYPTO_SIGN_SEEDBYTES) {
            $keypair = sodium_crypto_sign_seed_keypair($raw);
            return sodium_crypto_sign_secretkey($keypair);
        }

        // Try raw base64
        $decoded = base64_decode(trim($raw), true);
        if ($decoded !== false) {
            if (strlen($decoded) === SODIUM_CRYPTO_SIGN_SEEDBYTES) {
                $keypair = sodium_crypto_sign_seed_keypair($decoded);
                return sodium_crypto_sign_secretkey($keypair);
            }
            if (strlen($decoded) === SODIUM_CRYPTO_SIGN_SECRETKEYBYTES) {
                return $decoded;
            }
            try {
                return self::extractFromDer($decoded);
            } catch (Throwable) {
                // fallback to general error below
            }
        }

        throw new AuthenticationException("Invalid private key format: Unable to parse Ed25519 key");
    }

    /**
     * Parses a PEM formatted key.
     *
     * @throws AuthenticationException
     */
    private static function parsePem(string $pem): string
    {
        if (str_contains($pem, 'RSA PRIVATE KEY')) {
            throw new AuthenticationException("The provided key is not an Ed25519 private key (found RSA key).");
        }

        $cleaned = preg_replace('/-----[^-]+-----/', '', $pem);
        if ($cleaned === null) {
            throw new AuthenticationException("Invalid private key format: Corrupted PEM delimiters");
        }

        $der = base64_decode(trim($cleaned), true);
        if ($der === false || $der === '') {
            throw new AuthenticationException("Invalid private key format: Base64 decode failed");
        }

        return self::extractFromDer($der);
    }

    /**
     * Extracts 32-byte seed from PKCS#8 DER bytes and builds a sodium secret key.
     *
     * @throws AuthenticationException
     */
    private static function extractFromDer(string $der): string
    {
        $hex = bin2hex($der);

        // Check if DER contains the Ed25519 OID
        if (!str_contains($hex, self::ED25519_OID_HEX)) {
            throw new AuthenticationException("The provided key is not an Ed25519 private key.");
        }

        // Standard PKCS#8 v1 structure
        $prefix = hex2bin(self::ED25519_PKCS8_PREFIX_HEX);
        if (str_starts_with($der, $prefix) && strlen($der) >= 48) {
            $seed = substr($der, 16, 32);
            $keypair = sodium_crypto_sign_seed_keypair($seed);
            return sodium_crypto_sign_secretkey($keypair);
        }

        // Search for OCTET STRING containing the 32-byte key after OID
        $oidPos = strpos($der, hex2bin(self::ED25519_OID_HEX));
        if ($oidPos !== false) {
            // In PKCS#8: AlgorithmIdentifier is followed by OCTET STRING (04) containing OCTET STRING (04 20 [32-byte seed])
            $pattern = hex2bin('0420');
            $keyPos = strpos($der, $pattern, $oidPos);
            if ($keyPos !== false && strlen($der) >= $keyPos + 2 + 32) {
                $seed = substr($der, $keyPos + 2, 32);
                $keypair = sodium_crypto_sign_seed_keypair($seed);
                return sodium_crypto_sign_secretkey($keypair);
            }
        }

        throw new AuthenticationException("Invalid private key format: Could not extract Ed25519 key from DER");
    }

    /**
     * Builds the exact canonical signature message string for Revolut X:
     * {timestamp}{METHOD}{path}{query_string}{body}
     *
     * @param string $timestampMs Current timestamp in milliseconds.
     * @param string $method HTTP method (GET, POST, DELETE, etc.).
     * @param string $path Request path (starts with /api).
     * @param array<string, mixed>|null $params Query parameters.
     * @param mixed $body Request body (array/object will be minified JSON).
     */
    public static function buildSignatureMessage(
        string $timestampMs,
        string $method,
        string $path,
        ?array $params = null,
        mixed $body = null
    ): string {
        $methodUpper = strtoupper($method);
        $normalizedPath = str_starts_with($path, '/api') ? $path : '/api' . $path;

        $queryString = '';
        if ($params !== null && !empty($params)) {
            $filtered = [];
            foreach ($params as $k => $v) {
                if ($v !== null) {
                    $filtered[(string)$k] = (string)$v;
                }
            }
            ksort($filtered);
            $parts = [];
            foreach ($filtered as $k => $v) {
                $parts[] = urlencode($k) . '=' . urlencode($v);
            }
            $queryString = implode('&', $parts);
        }

        $bodyString = '';
        if ($body !== null) {
            if (is_array($body) || is_object($body)) {
                $encoded = json_encode($body, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
                $bodyString = $encoded !== false ? $encoded : '';
            } elseif (is_string($body)) {
                $bodyString = $body;
            }
        }

        return "{$timestampMs}{$methodUpper}{$normalizedPath}{$queryString}{$bodyString}";
    }

    /**
     * Signs a request and returns the necessary authentication headers:
     * - X-Revx-API-Key
     * - X-Revx-Timestamp
     * - X-Revx-Signature
     * - Content-Type (if body provided)
     *
     * @param string $apiKey Revolut X API key.
     * @param string $secretKey 64-byte sodium secret key.
     * @param string $method HTTP method.
     * @param string $path Request path.
     * @param array<string, mixed>|null $params Query parameters.
     * @param mixed $body Request body.
     * @return array<string, string>
     */
    public static function signRequest(
        string $apiKey,
        string $secretKey,
        string $method,
        string $path,
        ?array $params = null,
        mixed $body = null
    ): array {
        $timestampMs = (string) (int) (microtime(true) * 1000);

        $message = self::buildSignatureMessage(
            timestampMs: $timestampMs,
            method: $method,
            path: $path,
            params: $params,
            body: $body
        );

        $signatureBytes = sodium_crypto_sign_detached($message, $secretKey);
        $signatureB64 = base64_encode($signatureBytes);

        $headers = [
            'X-Revx-API-Key' => $apiKey,
            'X-Revx-Timestamp' => $timestampMs,
            'X-Revx-Signature' => $signatureB64,
        ];

        if ($body !== null) {
            $headers['Content-Type'] = 'application/json';
        }

        return $headers;
    }
}
