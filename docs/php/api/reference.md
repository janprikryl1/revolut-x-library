# PHP API Reference

Přehled tříd, rozhraní, pomocných nástrojů a výjimek v PHP SDK `janprikryl/revolutx`.

---

## 1. Hlavní klient: `RevolutX\Client`
*(Dostupný také pod aliasem `RevolutX\RevolutXClient`)*

### Konstruktor
```php
public function __construct(
    ?string $apiKey = null,
    ?string $privateKeyPath = null,
    ?string $privateKeyBytes = null,
    string $baseUrl = 'https://revx.revolut.com/api',
    string $apiVersion = '1.0',
    float $requestDelay = 0.85,
    int $timeout = 15,
    int $maxRetries = 3
)
```

### Veřejná tržní data (`MarketTrait`)
- `getPairs(): array` — Konfigurace a limity všech aktivních párů.
- `getPair(string $symbol): array` — Konfigurace konkrétního páru.
- `getCurrencies(): array` — Konfigurace podporovaných měn.
- `getTickers(): array` — Aktuální tickery všech párů.
- `getTicker(string $symbol): array` — Aktuální ticker zvoleného páru.
- `getOrderBook(string $symbol, int $depth = 10): array` — Kniha objednávek.
- `getCandles(string $symbol, int $interval = Interval::H1, ?int $since = null, ?int $until = null): array` — Svíčky OHLCV.
- `getTrades(string $symbol, int $limit = 100, ?string $before = null, ?string $after = null): array` — Veřejné obchody.

### Správa objednávek (`OrdersTrait`)
- `placeOrder(string|array $symbolOrPayload, ?string $side = null, string $orderType = OrderType::MARKET, ...): array` — Univerzální odeslání objednávky.
- `placeMarketOrder(string $symbol, string $side, ?string $baseSize = null, ?string $quoteSize = null, ?string $clientOrderId = null): array` — Tržní příkaz.
- `placeLimitOrder(string $symbol, string $side, string $price, ..., bool $postOnly = false, string $timeInForce = TimeInForce::GTC): array` — Limitní příkaz.
- `calculateMakerPrice(string $symbol, string $side, mixed $offset = '0.10', mixed $tickSize = '0.01'): string` — Výpočet bezpečné Maker ceny.
- `placeMakerOrder(string $symbol, string $side, ?string $price = null, mixed $offset = '0.10', mixed $tickSize = '0.01', ...): array` — Garantovaný Maker příkaz (0.00% poplatek).
- `getOrder(string $orderId): array` — Detail objednávky.
- `getOrderFills(string $orderId): array` — Jednotlivé exekuce objednávky.
- `getActiveOrders(?string $symbol = null): array` — Otevřené objednávky.
- `getHistoricalOrders(?string $symbol = null, int $limit = 50, ?string $cursor = null): array` — Historie objednávek.
- `cancelOrder(string $orderId): array` — Zrušení objednávky.
- `cancelAllOrders(?string $symbol = null): array` — Hromadné zrušení objednávek.

### Účetnictví & Peněženka (`AccountTrait`)
- `getBalances(): array` — Zůstatky všech měn.
- `getBalance(string $currency): array` — Zůstatek konkrétní měny.
- `getTransactions(int $limit = 50, ?string $cursor = null): array` — Transakční kniha (ledger).
- `getAccountTrades(string $symbol, int $limit = 50, ?string $cursor = null): array` — Historie vlastních obchodů.

---

## 2. Typy a Konstanty (`RevolutX\Types\*`)

- **`OrderSide`**: `OrderSide::BUY` (`'buy'`), `OrderSide::SELL` (`'sell'`).
- **`OrderType`**: `OrderType::MARKET` (`'market'`), `OrderType::LIMIT` (`'limit'`).
- **`TimeInForce`**: `TimeInForce::GTC` (`'gtc'`), `TimeInForce::IOC` (`'ioc'`), `TimeInForce::FOK` (`'fok'`).
- **`Interval`**: `Interval::M1` (1), `Interval::M5` (5), `Interval::M15` (15), `Interval::H1` (60), `Interval::H4` (240), `Interval::D1` (1440).
- **`FeeEstimate`**: DTO obsahující výpočet a popis poplatku.

---

## 3. Pomocné třídy (`RevolutX\Helpers\*`)

- **`MakerOrderStrategy`**: `calculateMakerPrice(string $side, mixed $bestBid = null, mixed $bestAsk = null, mixed $lastPrice = null, mixed $offset = '0.10', mixed $tickSize = '0.01'): string`
- **`FeeCalculator`**: `calculate(string $side, mixed $price, bool $isMaker, mixed $baseSize = null, mixed $quoteSize = null): FeeEstimate`
- **`OrderPayloadBuilder`**: Sestavování a validace JSON payloadů objednávek.
- **`SymbolNormalizer`**: Normalizace názvů párů (`BTC/EUR` $\rightarrow$ `BTC-EUR`).

---

## 4. Výjimky (`RevolutX\Exceptions\*`)

```text
RevolutXException (bázová třída)
├── AuthenticationException    — Chybějící klíče, neplatný PEM nebo HTTP 401/403
├── RateLimitException         — Překročení limitu (HTTP 429), obsahuje getRetryAfterSeconds()
├── ApiException               — Ostatní chyby API s getStatusCode(), getErrorCode()
├── OrderValidationException   — Neplatné parametry před odesláním
└── NetworkException           — Timeout, selhání cURL spojení
```
