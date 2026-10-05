# Account & Balances Guide

The `revolut-x-python` SDK provides methods to inspect wallet balances, transaction ledgers, and executed trade histories.

---

## Balances

Fetch all balances across all currencies:

```python
from revolut_x import RevolutXClient

client = RevolutXClient(api_key="...", private_key_path="keys/private.pem")

balances = client.get_balances()
for b in balances:
    if float(b["total"]) > 0:
        print(f"{b['currency']}: Available = {b['available']}, In Orders = {b['reserved']}, Total = {b['total']}")
```

Query a specific currency balance:

```python
eur = client.get_balance("EUR")
print(f"Available EUR: {eur['available']}")

btc = client.get_balance("BTC")
print(f"Available BTC: {btc['available']}")
```

---

## Transactions (Ledger)

Retrieve deposits, withdrawals, trade settlements, and fee charges:

```python
transactions, next_cursor = client.get_transactions(limit=10)

for tx in transactions:
    src = tx.get("source", {})
    dst = tx.get("destination", {})
    print(f"{tx.get('created_date')}: {src.get('amount')} {src.get('currency')} -> {dst.get('amount')} {dst.get('currency')}")
```

---

## Private Trade History

Inspect personal executed trades with exact fee details:

```python
trades, next_cursor = client.get_account_trades("BTC-EUR", limit=10)

for t in trades:
    print(f"[{t.get('side', t.get('s'))}] {t.get('quantity', t.get('q'))} BTC @ {t.get('price', t.get('p'))} EUR")
```
