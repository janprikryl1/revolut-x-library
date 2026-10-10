# Ed25519 Authentication and Request Signing

The Revolut X REST API requires every request to all private endpoints (order placement, account balances, trade history) to be cryptographically signed using the asymmetric **Ed25519** algorithm (RFC 8032 / Edwards-curve Digital Signature Algorithm).

---

## Canonical Message Format

The message to be signed is composed of 5 parts in exactly this order:

$$\text{message} = \text{timestamp} + \text{METHOD} + \text{path} + \text{query\_string} + \text{body}$$

1. **`timestamp`** — Current time in milliseconds since the epoch (Unix timestamp in ms). Must fall within the exchange's tolerance window relative to server time.
2. **`METHOD`** — The HTTP method normalised to uppercase (`GET`, `POST`, `DELETE`).
3. **`path`** — The relative endpoint path, normalised so that it starts with the `/api` prefix (e.g. `/api/1.0/orders`).
4. **`query_string`** — Alphabetically sorted query parameters joined by `&`, where both key and value are URL-encoded. If no parameters are present, the string is empty.
5. **`body`** — The minified JSON request body with no extra whitespace after separators (`,`, `:`). If no body is present, the string is empty.

---

## Required HTTP Headers

Every authenticated request must include the following headers:

- `X-Revx-API-Key` — Your public API key from the Revolut X account settings.
- `X-Revx-Timestamp` — The millisecond timestamp, identical to the one used in the signature message.
- `X-Revx-Signature` — The 64-byte Ed25519 signature of the message, Base64-encoded.
- `Content-Type: application/json` — Only when the request carries a body (e.g. POST).

---

## SDK Implementation

Both SDKs in this repository handle the entire procedure fully automatically:

=== "Python"

    In Python, signing is implemented in the `revolut_x._auth` module using the standard `cryptography` library:

    ```python
    from revolut_x import RevolutXClient

    client = RevolutXClient(
        api_key="your-api-key",
        private_key_path="keys/private.pem",
    )
    # All orders/balances calls are signed automatically:
    balances = client.get_balances()
    ```

=== "PHP"

    In PHP, signing is implemented in the `RevolutX\Auth\Signer` class using the native `ext-sodium` extension (`sodium_crypto_sign_detached`):

    ```php
    use RevolutX\Client;

    $client = new Client(
        apiKey: 'your-api-key',
        privateKeyPath: 'keys/private.pem'
    );
    // All orders/balances calls are signed automatically:
    $balances = $client->getBalances();
    ```

---

## Generating an Ed25519 Key Pair

To generate a new private key in the standard PKCS#8 PEM format, you can use OpenSSL:

```bash
openssl genpkey -algorithm ed25519 -out keys/private.pem
openssl pkey -in keys/private.pem -pubout -out keys/public.pem
```

Upload the public key `keys/public.pem` to the settings of your **Revolut X** account, where the matching `API Key` will be generated for you.
