# Order Management Guide

Revolut X allows placing, querying, and canceling orders via authenticated API endpoints.

---

## Placing Orders

You can size orders either in **Quote Currency** (e.g. EUR) or in **Base Currency** (e.g. BTC).

### 1. Zero-Fee Maker Limit Orders (`post_only=True`)
To guarantee execution with **0.00% Maker fees**, set `post_only=True`:

```python
from revolut_x import RevolutXClient, OrderSide, TimeInForce

client = RevolutXClient(api_key="...", private_key_path="keys/private.pem")

# Buy BTC for 50 EUR at limit price 70,000 EUR
order = client.place_limit_order(
    symbol="BTC-EUR",
    side=OrderSide.BUY,
    price="70000.00",
    quote_size="50.00",
    post_only=True,
    time_in_force=TimeInForce.GTC,
)

print(f"Order submitted: ID = {order['venue_order_id']}, State = {order['state']}")
```

### 2. Immediate Market Orders (Taker: 0.09%)

```python
# Market buy spending 100 EUR
market_buy = client.place_market_order(
    symbol="BTC-EUR",
    side=OrderSide.BUY,
    quote_size="100.00",
)

# Market sell selling exactly 0.002 BTC
market_sell = client.place_market_order(
    symbol="BTC-EUR",
    side=OrderSide.SELL,
    base_size="0.002",
)
```

---

## Inspecting Orders and Fills

### Querying an Order by ID
```python
detail = client.get_order(order["venue_order_id"])

print(f"Status:          {detail['status']}")
print(f"Filled Quantity: {detail['filled_quantity']} BTC")
print(f"Total Fee:       {detail['total_fee']} {detail.get('fee_currency', 'EUR')}")
```

### Querying Fills (Partial Executions)
```python
fills = client.get_order_fills(order["venue_order_id"])
for fill in fills:
    fee_type = "Maker (0%)" if fill.get("im") else "Taker (0.09%)"
    print(f"Filled {fill['q']} BTC @ {fill['p']} EUR [{fee_type}]")
```

### Active and Historical Orders
```python
# All active orders
active_orders = client.get_active_orders(symbol="BTC-EUR")

# Paginated history
history, next_cursor = client.get_historical_orders(symbol="BTC-EUR", limit=20)
```

---

## Canceling Orders

```python
# Cancel single order
client.cancel_order(order["venue_order_id"])

# Cancel all open orders for a pair
client.cancel_all_orders(symbol="BTC-EUR")

# Cancel all open orders across all pairs
client.cancel_all_orders()
```
