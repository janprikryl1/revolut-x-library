# PHP Průvodce: Tržní data

Revolut X poskytuje veřejné koncové body pro čtení konfigurací trhů, cenových tickerů, hloubky trhu (order book) a historických svíček (OHLCV).

---

## 1. Měnové páry a konfigurace

```php
use RevolutX\Client;

$client = new Client();

// Získání všech aktivních párů
$pairs = $client->getPairs();

// Detail konkrétního páru
$btcEur = $client->getPair('BTC-EUR');
echo "Minimální velikost objednávky: " . $btcEur['min_order_size'] . " BTC\n";
echo "Cenový krok: " . $btcEur['quote_step'] . " EUR\n";
```

---

## 2. Cenové tickery

Tickery vracejí aktuální nejlepší nabídku (`bid`), nejlepší poptávku (`ask`) a cenu posledního obchodu (`last_price`):

```php
// Ticker pro jeden pár
$ticker = $client->getTicker('BTC-EUR');
echo "Bid: {$ticker['bid']} EUR | Ask: {$ticker['ask']} EUR\n";

// Všechny tickery
$allTickers = $client->getTickers();
```

---

## 3. Kniha objednávek (Order Book)

```php
// Stažení hloubky trhu pro BTC-EUR (top 10 úrovní)
$orderBook = $client->getOrderBook('BTC-EUR', depth: 10);

echo "Nejlepší nabídka (Bid 1): " . $orderBook['bids'][0][0] . " EUR (objem: " . $orderBook['bids'][0][1] . " BTC)\n";
echo "Nejlepší poptávka (Ask 1): " . $orderBook['asks'][0][0] . " EUR (objem: " . $orderBook['asks'][0][1] . " BTC)\n";
```

---

## 4. Svíčková data (OHLCV)

Podporované časové rámce jsou definovány ve třídě `Interval`:

| Konstanta | Hodnota (minuty) | Popis |
| :--- | :--- | :--- |
| `Interval::M1` | `1` | 1 minuta |
| `Interval::M5` | `5` | 5 minut |
| `Interval::M15` | `15` | 15 minut |
| `Interval::H1` | `60` | 1 hodina |
| `Interval::H4` | `240` | 4 hodiny |
| `Interval::D1` | `1440` | 1 den |

```php
use RevolutX\Types\Interval;

$candles = $client->getCandles('BTC-EUR', interval: Interval::H1);

foreach (array_slice($candles, -5) as $candle) {
    echo "Čas: {$candle['start']} | Open: {$candle['open']} | Close: {$candle['close']} | Objem: {$candle['volume']}\n";
}
```
