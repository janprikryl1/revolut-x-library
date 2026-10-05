# Revolut X Multi-Language SDK
<em>Oficiální dokumentace SDK pro REST API kryptoměnové burzy Revolut X (v1.0) v jazycích Python a PHP.</em>

---

## Přehled projektu

Tento repozitář představuje multi-jazykovou knihovnu (SDK) vytvořenou pro interakci s **Revolut X Crypto Exchange REST API (v1.0)**. Knihovna pokrývá veškeré veřejné i autentizované endpointy, automatizuje kryptografické podepisování přes **Ed25519**, řeší rate-limiting burzy a přináší optimalizační strategii pro nulové poplatky (**0.00% Maker poplatek**).

Knihovna vznikla jako součást **diplomové práce** na **VŠB – Technické univerzitě Ostrava** (Fakulta elektrotechniky a informatiky).

- **Autor**: Bc. Jan Přikryl
- **Instituce**: VŠB – Technická univerzita Ostrava, FEI
- **API Version**: `1.0` (Revolut X REST API)
- **Repozitář**: [github.com/janprikryl1/revolut-x-library](https://github.com/janprikryl1/revolut-x-library)

---

## Podporované jazyky & SDK

| Jazyk | Složka | Balíček | Stav | Minimální verze |
| :--- | :--- | :--- | :--- | :--- |
| **Python** | [`python/`](https://github.com/janprikryl1/revolut-x-library/tree/main/python) | `revolut-x-python` | Stabilní (`v0.0.6`) | Python 3.10+ |
| **PHP** | [`php/`](https://github.com/janprikryl1/revolut-x-library/tree/main/php) | `janprikryl/revolutx` | Stabilní (`v0.1.0`) | PHP 8.0+ / 8.1+ |

---

## Hlavní přednosti architektury

1. **Plná podpora Revolut X API v1.0** — Kompletní sada metod pro tržní data (tickery, kniha objednávek, svíčky OHLCV, veřejné obchody), správu objednávek a účetnictví.
2. **Kryptografické Ed25519 podepisování**:
   - V **Pythonu** pomocí knihovny `cryptography` (PKCS#8 PEM).
   - V **PHP** pomocí nativního rozšíření `ext-sodium` s nulovými externími závislostmi.
3. **Smart Maker Order Strategy (0.00% poplatek)** — Vestavěná kalkulace cenových offsetů a parametr `post_only=true` pro garantované zadávání příkazů s nulovým poplatkem (oproti 0.09% u Taker příkazů).
4. **Respektování rate limitů** — Automatické zpoždění požadavků (1 req/s na veřejných endpointech) a transparentní zpracování HTTP 429 s hlavičkou `Retry-After`.
5. **Jednotný design (DX)** — Obě SDK sdílejí identické pojmenování parametrů, strukturu návratových hodnot a koncepci hierarchie výjimek.
6. **AI Agent Integrace** — Připravený skill pro AI agenty (Google Antigravity, Claude, Cursor) pro automatizaci burzovních operací.

---

## Rychlé srovnání kódu

=== "Python"

    ```python
    from revolut_x import RevolutXClient, OrderSide

    client = RevolutXClient(
        api_key="your-api-key",
        private_key_path="keys/private.pem",
    )

    # 1. Ticker
    ticker = client.get_ticker("BTC-EUR")
    print(f"BTC Cena: {ticker['last_price']} EUR")

    # 2. Maker příkaz s 0% poplatkem
    order = client.place_maker_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        quote_size="50.00",
        offset="0.10",
    )
    print(f"Order ID: {order['venue_order_id']}")
    ```

=== "PHP"

    ```php
    use RevolutX\Client;
    use RevolutX\Types\OrderSide;

    $client = new Client(
        apiKey: 'your-api-key',
        privateKeyPath: 'keys/private.pem'
    );

    // 1. Ticker
    $ticker = $client->getTicker('BTC-EUR');
    echo "BTC Cena: " . $ticker['last_price'] . " EUR\n";

    // 2. Maker příkaz s 0% poplatkem
    $order = $client->placeMakerOrder(
        symbol: 'BTC-EUR',
        side: OrderSide::BUY,
        quoteSize: '50.00',
        offset: '0.10'
    );
    echo "Order ID: " . $order['venue_order_id'] . "\n";
    ```
