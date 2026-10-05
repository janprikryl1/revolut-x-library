<?php

declare(strict_types=1);

namespace RevolutX\Tests;

use RevolutX\Client;
use RevolutX\Exceptions\AuthenticationException;
use RevolutX\RevolutXClient;
use PHPUnit\Framework\TestCase;

class ClientTest extends TestCase
{
    public function testInstantiatePublicClient(): void
    {
        $client = new Client();
        $this->assertFalse($client->isAuthenticated());
    }

    public function testInstantiateAliasClass(): void
    {
        $client = new RevolutXClient();
        $this->assertInstanceOf(Client::class, $client);
        $this->assertFalse($client->isAuthenticated());
    }

    public function testInstantiateAuthenticatedClientWithRawKey(): void
    {
        $keypair = sodium_crypto_sign_keypair();
        $secretKey = sodium_crypto_sign_secretkey($keypair);

        $client = new Client(
            apiKey: 'my-api-key',
            privateKeyBytes: $secretKey
        );

        $this->assertTrue($client->isAuthenticated());
    }

    public function testAuthenticatedEndpointThrowsWhenNotAuthenticated(): void
    {
        $client = new Client();

        $this->expectException(AuthenticationException::class);
        $this->expectExceptionMessage('requires authentication');

        $client->getBalances();
    }
}
