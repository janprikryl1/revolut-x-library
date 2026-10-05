# PHP Průvodce: Správa objednávek

Modul objednávek umožňuje zadávat tržní i limitní příkazy, kontrolovat stav rozpracovaných objednávek a rušit aktivní pokyny.

---

## 1. Tržní objednávka (Market Order)

Tržní objednávka se páruje okamžitě za nejlepší dostupnou cenu v knize (Taker poplatek 0.09%). Zadávejte buď `quoteSize` (hodnota v EUR) nebo `baseSize` (množství v BTC):

```php
use RevolutX\Client;
use RevolutX\Types\OrderSide;

$client = new Client(apiKey: '...', privateKeyPath: 'keys/private.pem');

// Nákup BTC za 50.00 EUR
$order = $client->placeMarketOrder(
    symbol: 'BTC-EUR',
    side: OrderSide::BUY,
    quoteSize: '50.00'
);

echo "Příkaz odeslán. ID: " . $order['venue_order_id'] . "\n";
```

---

## 2. Limitní objednávka (Limit Order)

Limitní objednávka čeká v knize na dosažení zadané ceny. Pro garanci nulového poplatku použijte `postOnly: true`:

```php
use RevolutX\Types\OrderSide;
use RevolutX\Types\TimeInForce;

$order = $client->placeLimitOrder(
    symbol: 'BTC-EUR',
    side: OrderSide::BUY,
    price: '75000.00',
    quoteSize: '100.00',
    postOnly: true,
    timeInForce: TimeInForce::GTC
);
```

---

## 3. Zjištění stavu a exekuce objednávky

```php
// Detail objednávky podle venue_order_id
$detail = $client->getOrder('7a52e92e-8639-4fe1-abaa-68d3a2d5234b');
echo "Stav: " . $detail['status'] . "\n";
echo "Vyplněno: " . $detail['filled_size'] . "\n";

// Získání jednotlivých exekucí (fills) a ověření maker statusu
$fills = $client->getOrderFills('7a52e92e-8639-4fe1-abaa-68d3a2d5234b');
foreach ($fills as $fill) {
    $feeType = $fill['im'] ? 'Maker (0.00%)' : 'Taker (0.09%)';
    echo "Cena: {$fill['p']} EUR, Objem: {$fill['q']}, Poplatek: {$feeType}\n";
}
```

---

## 4. Aktivní objednávky a rušení

```php
// Seznam všech otevřených příkazů
$activeOrders = $client->getActiveOrders('BTC-EUR');

// Zrušení konkrétního příkazu
$client->cancelOrder('7a52e92e-8639-4fe1-abaa-68d3a2d5234b');

// Zrušení všech otevřených příkazů pro daný měnový pár
$client->cancelAllOrders('BTC-EUR');
```
