# Autentizace a podepisování Ed25519

Revolut X REST API vyžaduje pro všechny soukromé koncové body (zadávání objednávek, zůstatky na účtu, historie obchodů) kryptografické podepisování každého požadavku pomocí asymetrického algoritmu **Ed25519** (RFC 8032 / Edwards-curve Digital Signature Algorithm).

---

## Formát kanonické zprávy

Zpráva k podpisu je složena z 5 částí v přesném pořadí:

$$\text{message} = \text{timestamp} + \text{METHOD} + \text{path} + \text{query\_string} + \text{body}$$

1. **`timestamp`** — Aktuální čas v milisekundách od epochy (Unix timestamp v ms). Musí být v toleranci burzy vůči času serveru.
2. **`METHOD`** — Velkými písmeny normalizovaná HTTP metoda (`GET`, `POST`, `DELETE`).
3. **`path`** — Relativní cesta endpointu, normalizovaná tak, aby začínala předponou `/api` (např. `/api/1.0/orders`).
4. **`query_string`** — Abecedně seřazené parametry dotazu oddělené znakem `&`, kde klíč i hodnota jsou zakódovány podle standardu URL encode. Pokud parametry nejsou přítomny, řetězec je prázdný.
5. **`body`** — Minifikované tělo požadavku ve formátu JSON bez přebytečných mezer za oddělovači (`,`, `:`). Pokud tělo není přítomno, řetězec je prázdný.

---

## Požadované HTTP hlavičky

Každý autentizovaný požadavek musí obsahovat následující hlavičky:

- `X-Revx-API-Key` — Váš veřejný API klíč z nastavení účtu Revolut X.
- `X-Revx-Timestamp` — Časová značka v milisekundách shodná se značkou použitou ve zprávě podpisu.
- `X-Revx-Signature` — 64bajtový Ed25519 podpis zprávy zakódovaný do Base64.
- `Content-Type: application/json` — Pouze v případě, že požadavek nese tělo (např. POST).

---

## Implementace v SDK

Obě SDK v repozitáři řeší celou proceduru plně automaticky:

=== "Python"

    V Pythonu je podepisování implementováno v modulu `revolut_x._auth` s využitím standardní knihovny `cryptography`:

    ```python
    from revolut_x import RevolutXClient

    client = RevolutXClient(
        api_key="your-api-key",
        private_key_path="keys/private.pem",
    )
    # Všechna volání orders/balances jsou automaticky podepsána:
    balances = client.get_balances()
    ```

=== "PHP"

    V PHP je podepisování implementováno ve třídě `RevolutX\Auth\Signer` s využitím nativního rozšíření `ext-sodium` (`sodium_crypto_sign_detached`):

    ```php
    use RevolutX\Client;

    $client = new Client(
        apiKey: 'your-api-key',
        privateKeyPath: 'keys/private.pem'
    );
    // Všechna volání orders/balances jsou automaticky podepsána:
    $balances = $client->getBalances();
    ```

---

## Generování klíčového páru Ed25519

Pro vygenerování nového privátního klíče ve standardním formátu PKCS#8 PEM lze použít OpenSSL:

```bash
openssl genpkey -algorithm ed25519 -out keys/private.pem
openssl pkey -in keys/private.pem -pubout -out keys/public.pem
```

Veřejný klíč `keys/public.pem` nahrajte do administrace svého účtu na **Revolut X**, kde vám bude vygenerován příslušný `API Key`.
