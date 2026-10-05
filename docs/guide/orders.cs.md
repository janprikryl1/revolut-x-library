# Uživatelská příručka: Správa objednávek

Revolut X umožňuje zadávat, sledovat a rušit objednávky prostřednictvím autentizovaných koncových bodů API.

---

## Zadávání objednávek

Objednávky můžete zadávat buď v **kótované měně** (např. EUR), nebo v **základní měně** (např. BTC).

### 1. Sjednocená metoda `place_order` (Doporučeno)
Můžete použít sjednocenou metodu `place_order` a specifikovat `order_type`:

```python
from revolut_x import RevolutXClient, OrderSide, OrderType

client = RevolutXClient(api_key="...", private_key_path="keys/private.pem")

# Tržní objednávka (Market)
order = client.place_order(
    "BTC-EUR",
    OrderSide.BUY,
    order_type=OrderType.MARKET,
    quote_size="50.00",
)

# Limitní objednávka (Maker post-only)
order = client.place_order(
    "BTC-EUR",
    OrderSide.BUY,
    order_type=OrderType.LIMIT,
    price="70000.00",
    quote_size="50.00",
    post_only=True,
)
```

### 2. Smart Maker objednávky bez poplatku (`place_maker_order`)
Revolut X účtuje **0.00% poplatek za Maker objednávky** (objednávky, které vstupují do knihy objednávek a poskytují likviditu).

Pomocí metody `place_maker_order` SDK automaticky určí optimální limitní cenu dotazem na živou knihu objednávek (`best_bid` / `best_ask`) a aplikuje bezpečnostní `offset` (výchozí: 0.10 EUR). Tím je zaručeno, že objednávka vstoupí do knihy bez okamžité kolize s existujícími kotacemi, a kvalifikuje se na **0.00% poplatek**:

- **NÁKUP (BUY):** `price = best_bid - offset`
- **PRODEJ (SELL):** `price = best_ask + offset`

```python
from revolut_x import RevolutXClient, OrderSide

client = RevolutXClient(api_key="...", private_key_path="keys/private.pem")

# 1. Nákup BTC za 50 EUR za optimální Maker cenu (0.00% poplatek)
order = client.place_maker_order(
    symbol="BTC-EUR",
    side=OrderSide.BUY,
    quote_size="50.00",
    offset="0.10",  # 10 centů pod nejlepší bid
)

# 2. Prodej 0.001 BTC za optimální Maker cenu (0.00% poplatek)
order = client.place_maker_order(
    symbol="BTC-EUR",
    side=OrderSide.SELL,
    base_size="0.001",
    offset="0.10",  # 10 centů nad nejlepší ask
)
```

Optimální Maker cenu si můžete předem spočítat a zkontrolovat i bez odeslání objednávky:

```python
# Zjištění optimální ceny bez odeslání objednávky
price = client.calculate_maker_price("BTC-EUR", OrderSide.BUY, offset="0.10")
print(f"Optimální Maker nákupní cena: {price} EUR")
```

### 3. Ruční limitní objednávky s vlastní cenou
Pokud chcete zadat limitní objednávku s pevnou cenou a zajistit **0.00% Maker poplatek**, použijte `order_type=OrderType.LIMIT` s parametrem `post_only=True`:

```python
from revolut_x import RevolutXClient, OrderSide, OrderType, TimeInForce

# Nákup BTC za 50 EUR při limitní ceně 70 000 EUR
order = client.place_order(
    symbol="BTC-EUR",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    price="70000.00",
    quote_size="50.00",
    post_only=True,
    time_in_force=TimeInForce.GTC,
)

print(f"Objednávka odeslána: ID = {order['venue_order_id']}, Stav = {order['state']}")
```

### 4. Okamžité tržní objednávky (0.09% Taker poplatek)
Pro okamžité provedení proti stávající knize objednávek použijte `order_type=OrderType.MARKET`:

```python
from revolut_x import RevolutXClient, OrderSide, OrderType

# Tržní nákup za 100 EUR
market_buy = client.place_order(
    symbol="BTC-EUR",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    quote_size="100.00",
)

# Tržní prodej přesně 0.002 BTC
market_sell = client.place_order(
    symbol="BTC-EUR",
    side=OrderSide.SELL,
    order_type=OrderType.MARKET,
    base_size="0.002",
)
```

---

## Kontrola objednávek a exekucí

### Dotaz na detail objednávky podle ID
```python
detail = client.get_order(order["venue_order_id"])

print(f"Stav:             {detail['status']}")
print(f"Vyplněný objem:   {detail['filled_quantity']} BTC")
print(f"Celkový poplatek: {detail['total_fee']} {detail.get('fee_currency', 'EUR')}")
```

### Zjištění dílčích exekucí (Fills)
```python
fills = client.get_order_fills(order["venue_order_id"])
for fill in fills:
    fee_type = "Maker (0%)" if fill.get("im") else "Taker (0.09%)"
    print(f"Vyplněno {fill['q']} BTC @ {fill['p']} EUR [{fee_type}]")
```

### Aktivní a historické objednávky
```python
# Všechny aktivní objednávky
active_orders = client.get_active_orders(symbol="BTC-EUR")

# Stránkovaná historie objednávek
history, next_cursor = client.get_historical_orders(symbol="BTC-EUR", limit=20)
```

---

## Rušení objednávek

```python
# Zrušení jedné konkrétní objednávky
client.cancel_order(order["venue_order_id"])

# Zrušení všech otevřených objednávek pro daný pár
client.cancel_all_orders(symbol="BTC-EUR")

# Zrušení všech otevřených objednávek napříč všemi páry
client.cancel_all_orders()
```
