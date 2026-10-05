# Uživatelská příručka: Veřejná tržní data

Revolut X poskytuje veřejné koncové body pro čtení konfigurací trhů, cenových tickerů, hloubky trhu (order book) a historických svíček (OHLCV) bez nutnosti autentizace.

---

## Tickery a kniha objednávek

### Získání tickerů
Můžete načíst tickery pro všechny aktivní měnové páry nebo pro jeden konkrétní:

```python
from revolut_x import RevolutXClient

client = RevolutXClient()

# Ticker pro jeden pár
ticker = client.get_ticker("BTC-EUR")
print(f"Poslední cena: {ticker['last_price']} EUR")
print(f"Nejlepší Bid:  {ticker['bid']} EUR")
print(f"Nejlepší Ask:  {ticker['ask']} EUR")

# Všechny tickery
all_tickers = client.get_tickers()
for t in all_tickers[:3]:
    print(f"{t['symbol']}: {t.get('last_price')}")
```

### Získání knihy objednávek (Order Book)
Načte aktuální cenové hladiny nákupních (bids) a prodejních (asks) příkazů do hloubky $N$:

```python
book = client.get_order_book("BTC-EUR", depth=5)

print("Top 5 Bids (Kupující):")
for price, qty in book["bids"][:5]:
    print(f"  {price} EUR x {qty} BTC")

print("\nTop 5 Asks (Prodávající):")
for price, qty in book["asks"][:5]:
    print(f"  {price} EUR x {qty} BTC")
```

---

## Cenové svíčky (OHLCV)

### Načtení jedné dávky
Burza podporuje časová rozlišení od 1 minuty do 4 týdnů:

```python
from revolut_x import RevolutXClient, Interval

client = RevolutXClient()

# 1-hodinové svíčky
candles = client.get_candles(
    "BTC-EUR",
    interval=Interval.HOUR_1,
    since=1700000000000
)

for c in candles[-5:]:
    print(f"Čas: {c['start']} | Open: {c['open']} | High: {c['high']} | Close: {c['close']}")
```

### Streamování dlouhých časových oken pomocí `iter_candles()`
API omezuje jednotlivý požadavek na 1000 svíček. Pro stahování delších kontinuálních období použijte generátor `iter_candles()`, který automaticky dělí časová okna:

```python
import time
from revolut_x import RevolutXClient, Interval

client = RevolutXClient()

# Stažení 1-minutových dat za posledních 30 dní
start_ms = int(time.time() * 1000) - (30 * 24 * 3600 * 1000)

count = 0
for candle in client.iter_candles("BTC-EUR", Interval.MIN_1, since=start_ms):
    count += 1
    # Zpracování svíčky...

print(f"Staženo {count} svíček.")
```
