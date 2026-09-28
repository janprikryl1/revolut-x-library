# Public Market Data Guide

Revolut X provides market data endpoints without requiring authentication.

---

## Tickers and Order Books

### Getting Tickers
You can fetch tickers for all active pairs or a single specific pair:

```python
from revolut_x import RevolutXClient

client = RevolutXClient()

# Single pair ticker
ticker = client.get_ticker("BTC-EUR")
print(f"Last Price: {ticker['last_price']} EUR")
print(f"Best Bid:   {ticker['bid']} EUR")
print(f"Best Ask:   {ticker['ask']} EUR")

# All tickers
all_tickers = client.get_tickers()
for t in all_tickers[:3]:
    print(f"{t['symbol']}: {t.get('last_price')}")
```

### Getting Order Books
Fetch the current bid and ask price levels up to depth $N$:

```python
book = client.get_order_book("BTC-EUR", depth=5)

print("Top 5 Bids (Buyers):")
for price, qty in book["bids"][:5]:
    print(f"  {price} EUR x {qty} BTC")

print("\nTop 5 Asks (Sellers):")
for price, qty in book["asks"][:5]:
    print(f"  {price} EUR x {qty} BTC")
```

---

## Candlesticks (OHLCV)

### Fetching a Single Batch
The exchange accepts interval resolutions from 1 minute up to 4 weeks:

```python
from revolut_x import RevolutXClient, Interval

client = RevolutXClient()

# 1-hour candles
candles = client.get_candles(
    "BTC-EUR",
    interval=Interval.HOUR_1,
    since=1700000000000
)

for c in candles[-5:]:
    print(f"Time: {c['start']} | Open: {c['open']} | High: {c['high']} | Close: {c['close']}")
```

### Streaming Long Time Ranges with `iter_candles()`
The API limits single requests to 1000 candles. To download continuous ranges, use the generator `iter_candles()` which automatically handles time window slicing:

```python
import time
from revolut_x import RevolutXClient, Interval

client = RevolutXClient()

# Download last 30 days of 1-minute data seamlessly
start_ms = int(time.time() * 1000) - (30 * 24 * 3600 * 1000)

count = 0
for candle in client.iter_candles("BTC-EUR", Interval.MIN_1, since=start_ms):
    count += 1
    # Process candle...

print(f"Streamed {count} candles.")
```
