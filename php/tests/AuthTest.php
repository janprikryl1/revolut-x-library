<?php

declare(strict_types=1);

namespace RevolutX\Tests;

use RevolutX\Auth\Signer;
use RevolutX\Exceptions\AuthenticationException;
use PHPUnit\Framework\TestCase;

class AuthTest extends TestCase
{
    public function testBuildSignatureMessageBasic(): void
    {
        $timestamp = '1710000000000';
        $method = 'GET';
        $path = '/api/1.0/orders';

        $msg = Signer::buildSignatureMessage(
            timestampMs: $timestamp,
            method: $method,
            path: $path
        );

        $this->assertSame('1710000000000GET/api/1.0/orders', $msg);

        // Lowercase method normalization
        $msgLower = Signer::buildSignatureMessage(
            timestampMs: $timestamp,
            method: 'get',
            path: $path
        );
        $this->assertSame('1710000000000GET/api/1.0/orders', $msgLower);
    }

    public function testBuildSignatureMessageWithParams(): void
    {
        $timestamp = '1710000000000';
        $method = 'GET';
        $path = '/api/1.0/orders';
        $params = [
            'symbol' => 'BTC/EUR',
            'limit' => 50,
            'after' => 'cursor_123',
            'empty_val' => null,
        ];

        $msg = Signer::buildSignatureMessage(
            timestampMs: $timestamp,
            method: $method,
            path: $path,
            params: $params
        );

        $expectedQuery = 'after=cursor_123&limit=50&symbol=BTC%2FEUR';
        $this->assertSame("1710000000000GET/api/1.0/orders{$expectedQuery}", $msg);
        $this->assertStringNotContainsString('empty_val', $msg);
    }

    public function testBuildSignatureMessageWithJsonBody(): void
    {
        $timestamp = '1710000000000';
        $method = 'POST';
        $path = '/api/1.0/orders';
        $body = [
            'client_order_id' => '4b68e984-6014-4112-9c3f-4e0730d43f07',
            'symbol' => 'BTC-EUR',
            'side' => 'buy',
            'order_configuration' => [
                'market' => [
                    'quote_size' => '50.00',
                ],
            ],
        ];

        $msg = Signer::buildSignatureMessage(
            timestampMs: $timestamp,
            method: $method,
            path: $path,
            body: $body
        );

        $expectedBody = json_encode($body, JSON_UNESCAPED_SLASHES);
        $this->assertSame("1710000000000POST/api/1.0/orders{$expectedBody}", $msg);
        $this->assertStringNotContainsString(': ', $msg);
        $this->assertStringNotContainsString(', ', $msg);
    }

    public function testBuildSignatureMessagePathNormalization(): void
    {
        $timestamp = '1710000000000';
        $method = 'GET';

        $msgWithout = Signer::buildSignatureMessage($timestamp, $method, '/1.0/orders');
        $msgWith = Signer::buildSignatureMessage($timestamp, $method, '/api/1.0/orders');

        $this->assertSame('1710000000000GET/api/1.0/orders', $msgWithout);
        $this->assertSame($msgWith, $msgWithout);
    }

    public function testLoadPrivateKeyFileNotFound(): void
    {
        $this->expectException(AuthenticationException::class);
        $this->expectExceptionMessage('Private key file not found');

        Signer::loadPrivateKey('/tmp/non_existent_key_file.pem');
    }

    public function testLoadPrivateKeyInvalidFormat(): void
    {
        $this->expectException(AuthenticationException::class);

        Signer::loadPrivateKey("-----BEGIN PRIVATE KEY-----\nNOT_BASE64\n-----END PRIVATE KEY-----");
    }

    public function testLoadPrivateKeyRejectsRsaKey(): void
    {
        $this->expectException(AuthenticationException::class);
        $this->expectExceptionMessage('not an Ed25519');

        Signer::loadPrivateKey("-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----");
    }

    public function testSignRequestReturnsCorrectHeadersAndValidSignature(): void
    {
        $keypair = sodium_crypto_sign_keypair();
        $secretKey = sodium_crypto_sign_secretkey($keypair);
        $publicKey = sodium_crypto_sign_publickey($keypair);

        $apiKey = 'test-api-key-123';
        $method = 'POST';
        $path = '/api/1.0/orders';
        $body = ['symbol' => 'BTC-EUR', 'side' => 'buy'];

        $headers = Signer::signRequest(
            apiKey: $apiKey,
            secretKey: $secretKey,
            method: $method,
            path: $path,
            body: $body
        );

        $this->assertArrayHasKey('X-Revx-API-Key', $headers);
        $this->assertArrayHasKey('X-Revx-Timestamp', $headers);
        $this->assertArrayHasKey('X-Revx-Signature', $headers);
        $this->assertArrayHasKey('Content-Type', $headers);

        $this->assertSame($apiKey, $headers['X-Revx-API-Key']);
        $this->assertTrue(ctype_digit($headers['X-Revx-Timestamp']));
        $this->assertSame('application/json', $headers['Content-Type']);

        // Verify base64 decoded length is 64 bytes
        $sigRaw = base64_decode($headers['X-Revx-Signature'], true);
        $this->assertNotFalse($sigRaw);
        $this->assertSame(64, strlen($sigRaw));

        // Mathematically verify signature with public key
        $expectedMessage = Signer::buildSignatureMessage(
            timestampMs: $headers['X-Revx-Timestamp'],
            method: $method,
            path: $path,
            body: $body
        );

        $verified = sodium_crypto_sign_verify_detached($sigRaw, $expectedMessage, $publicKey);
        $this->assertTrue($verified, 'Ed25519 signature verification must pass.');
    }
}
