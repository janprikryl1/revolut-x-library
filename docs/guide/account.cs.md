# Uživatelská příručka: Účet a zůstatky

Knihovna `revolut-x-python` poskytuje metody pro zjišťování zůstatků na peněženkách, transakční historie a přehledu provedených obchodů.

---

## Zůstatky na účtu

Načtení všech měnových zůstatků:

```python
from revolut_x import RevolutXClient

client = RevolutXClient(api_key="...", private_key_path="keys/private.pem")

balances = client.get_balances()
for b in balances:
    if float(b["total"]) > 0:
        print(f"{b['currency']}: Dostupné = {b['available']}, V objednávkách = {b['reserved']}, Celkem = {b['total']}")
```

Zjištění zůstatku pro jednu konkrétní měnu:

```python
eur = client.get_balance("EUR")
print(f"Dostupné EUR: {eur['available']}")

btc = client.get_balance("BTC")
print(f"Dostupné BTC: {btc['available']}")
```

---

## Transakce (Účetní kniha)

Získání historie vkladů, výběrů, vypořádání obchodů a poplatků:

```python
transactions, next_cursor = client.get_transactions(limit=10)

for tx in transactions:
    src = tx.get("source", {})
    dst = tx.get("destination", {})
    print(f"{tx.get('created_date')}: {src.get('amount')} {src.get('currency')} -> {dst.get('amount')} {dst.get('currency')}")
```

---

## Historie vlastních obchodů

Prohlížení historie provedených obchodů s přesnými informacemi o poplatcích:

```python
trades, next_cursor = client.get_account_trades("BTC-EUR", limit=10)

for t in trades:
    print(f"[{t.get('side', t.get('s'))}] {t.get('quantity', t.get('q'))} BTC @ {t.get('price', t.get('p'))} EUR")
```
