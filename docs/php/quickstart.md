# PHP SDK — Rychlý start

SDK pro PHP umožňuje plnou integraci s kryptoměnovou burzou Revolut X v moderním PHP 8.0+.

---

## Požadavky & Instalace

### Požadavky
- PHP verze `^8.0` (8.0.30+, 8.1, 8.2, 8.3, 8.4, 8.5)
- Rozšíření: `ext-curl`, `ext-json`, `ext-sodium`

### Instalace přes Composer

```bash
composer require janprikryl/revolutx
```

Nebo přímé zahrnutí v monorepu:

```bash
cd php
composer install
```

---

## Inicializace klienta

### 1. Veřejný režim (bez API klíče)
Pro stahování tržních dat, tickerů a knihy objednávek není potřeba žádná autentizace:

```php
use RevolutX\Client;

$client = new Client();
$ticker = $client->getTicker('BTC-EUR');
echo "Aktuální cena BTC: {$ticker['last_price']} EUR\n";
```

### 2. Autentizovaný režim (obchodování & účet)
Pro zadávání objednávek a přístup k peněžence předejte API klíč a cestu k privátnímu klíči:

```php
use RevolutX\Client;

$client = new Client(
    apiKey: 'your-api-key',
    privateKeyPath: 'keys/private.pem'
);

$balances = $client->getBalances();
print_r($balances);
```

---

## Konfigurační parametry

Při vytváření instance `Client` lze přizpůsobit následující volby:

| Parametr | Typ | Výchozí hodnota | Popis |
| :--- | :--- | :--- | :--- |
| `apiKey` | `?string` | `null` | Váš Revolut X API klíč. |
| `privateKeyPath` | `?string` | `null` | Cesta k souboru s Ed25519 privátním klíčem (`.pem`). |
| `privateKeyBytes` | `?string` | `null` | Přímo obsah PEM souboru nebo binární bajty klíče. |
| `baseUrl` | `string` | `'https://revx.revolut.com/api'` | Kořenová URL adresa API. |
| `requestDelay` | `float` | `0.85` | Minimální prodleva mezi požadavky v sekundách (ochrana před rate-limitem). |
| `timeout` | `int` | `15` | Timeout pro cURL v sekundách. |
| `maxRetries` | `int` | `3` | Maximální počet opakování při chybách 429 a 5xx. |
