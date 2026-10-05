# PHP Průvodce: Účet a zůstatky

Autentizované endpointy pro správu peněženek a audit transakcí.

---

## 1. Kontrola zůstatků

```php
use RevolutX\Client;

$client = new Client(apiKey: '...', privateKeyPath: 'keys/private.pem');

// Zůstatky všech měn na účtu
$balances = $client->getBalances();

foreach ($balances as $b) {
    if ((float)$b['total'] > 0) {
        echo "Měna: {$b['currency']} | Dostupné: {$b['available']} | Rezervováno: {$b['reserved']}\n";
    }
}

// Rychlé zjištění jedné měny
$eur = $client->getBalance('EUR');
echo "Disponibilní EUR: {$eur['available']}\n";
```

---

## 2. Transakční historie (Ledger)

Endpoint vrací vklady, výběry, poplatky a vypořádání obchodů s podporou kurzorového stránkování:

```php
$result = $client->getTransactions(limit: 20);
$transactions = $result['transactions'];
$nextCursor = $result['next_cursor'];

foreach ($transactions as $tx) {
    echo "ID: {$tx['id']} | Typ: {$tx['type']} | Částka: {$tx['amount']}\n";
}
```

---

## 3. Historie vlastních obchodů (Private Trades)

Na rozdíl od veřejných obchodů obsahuje kompletní informace o zaplacených poplatcích a exekucích:

```php
$history = $client->getAccountTrades('BTC-EUR', limit: 50);

foreach ($history['trades'] as $trade) {
    echo "Strana: {$trade['side']} | Cena: {$trade['price']} EUR | Objem: {$trade['quantity']}\n";
}
```
