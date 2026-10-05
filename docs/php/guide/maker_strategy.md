# PHP Průvodce: Smart Maker Strategie

Revolut X nabízí obchodování s nulovým poplatkem (**0.00% Maker**) pro příkazy, které tvoří trh. PHP SDK přináší kompletní nástroje pro bezpečné využití této výhody.

---

## 1. Automatické odeslání Maker objednávky

Metoda `placeMakerOrder` v jednom kroku:
1. Zjistí aktuální stav knihy objednávek (`bid` pro nákup, `ask` pro prodej).
2. Spočítá optimální limitní cenu s bezpečnostním posunem (`offset`).
3. Zaokrouhlí cenu na povolený krok trhu (`tickSize`).
4. Odešle příkaz s příznakem `postOnly: true`.

```php
use RevolutX\Client;
use RevolutX\Types\OrderSide;

$client = new Client(apiKey: '...', privateKeyPath: 'keys/private.pem');

// Nákup BTC za 50 EUR s nulovým poplatkem a offsetem 0.10 EUR
$order = $client->placeMakerOrder(
    symbol: 'BTC-EUR',
    side: OrderSide::BUY,
    quoteSize: '50.00',
    offset: '0.10',
    tickSize: '0.01'
);

echo "Maker příkaz zadán: " . $order['venue_order_id'] . "\n";
```

---

## 2. Samostatný výpočet ceny (`MakerOrderStrategy`)

Pokud chcete cenu spočítat předem v rámci vlastní obchodní logiky:

```php
use RevolutX\Helpers\MakerOrderStrategy;
use RevolutX\Types\OrderSide;

$price = MakerOrderStrategy::calculateMakerPrice(
    side: OrderSide::BUY,
    bestBid: '85200.00',
    offset: '0.20',
    tickSize: '0.01'
);

// Výsledek: "85199.80"
```

---

## 3. Kalkulace úspor na poplatcích (`FeeCalculator`)

Před odesláním objednávky si můžete vygenerovat přesný odhad a porovnání poplatků:

```php
use RevolutX\Helpers\FeeCalculator;
use RevolutX\Types\OrderSide;

$estimate = FeeCalculator::calculate(
    side: OrderSide::BUY,
    price: '85000.00',
    isMaker: true,
    quoteSize: '1000.00'
);

echo $estimate->explanation;
// Vypíše:
// Buy 0.01176471 BTC for 1000.00 EUR at price 85000.00.
// - Execution type: MAKER
// - Fee rate: 0.00 %
// - Fee amount: 0.0000 EUR
// - Net received approx: 0.01176471 BTC
```
