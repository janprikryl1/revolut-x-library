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
Načte aktuální cenové hladiny nákupních (bids) a prodejních (asks) příkazů.
Každá hladina je **slovník** — cena je pod klíčem `p`, množství pod `q`:

```python
book = client.get_order_book("BTC-EUR")

print("Bids (Kupující):")
for level in book["bids"]:
    print(f"  {level['p']} EUR x {level['q']} BTC")

print("\nAsks (Prodávající):")
for level in book["asks"]:
    print(f"  {level['p']} EUR x {level['q']} BTC")
```

!!! note "Hloubka knihy je fixní"
    Burza aktuálně vrací **5 hladin na každou stranu** a argument `depth`
    ignoruje — nespoléhejte se tedy na vyžádání hlubší knihy.

---

## Cenové svíčky (OHLCV)

!!! warning "Jak daleko do historie dosáhnete, určuje zvolený interval"
    Na svíčky se vztahují dva nezávislé limity a jen ten první umí knihovna
    obejít:

    - **1000 svíček na požadavek** — limit velikosti requestu. `iter_candles()`
      okno rozsekává a řeší to za vás.
    - **Retence historie** — jak dlouho burza dané rozlišení vůbec drží. Jemná
      rozlišení se promazávají a žádné stránkování je nevrátí.

    Dotaz mimo retenci **není chyba**. API odpoví HTTP 200 s prázdným seznamem,
    takže `iter_candles()` poslušně nevyjede nic a 30denní minutový cyklus
    prostě skončí s `Streamed 0 candles.`

    Naměřeno na `BTC-EUR` s `Interval.MIN_1`, dotaz na 500 svíček v rostoucím
    odstupu:

    | Začátek okna | Vrácených svíček |
    | --- | --- |
    | 2 dny zpět | 500 |
    | 7 dní zpět | 500 |
    | 14 dní zpět | 500 |
    | 30 dní zpět | 0 |

    Minutová data tedy dosáhnou za 14 dní, ale ne na 30, zatímco
    `Interval.HOUR_1` zvládne 30 dní bez problémů — čím hrubší interval, tím
    hlubší historie. Jde o naměřené chování, nikoli o garanci z dokumentace,
    takže to berte jako řádový odhad. **Pokud se stahování vrátí prázdné,
    zkuste nejdřív hrubší interval, než začnete hledat chybu ve vlastním kódu.**

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
API omezuje jednotlivý požadavek na 1000 svíček. Pro stahování delších kontinuálních období použijte generátor `iter_candles()`, který automaticky dělí časová okna. Rozšiřuje ale jen to, kolik dat můžete *vyžádat* — ne to, jak daleko do minulosti data existují (viz varování o retenci výše):

```python
import time
from revolut_x import RevolutXClient, Interval

client = RevolutXClient()

# Stažení 1-minutových dat za posledních 7 dní (10 080 svíček, tedy daleko
# za limitem 1000 na požadavek, ale stále v rámci retence)
start_ms = int(time.time() * 1000) - (7 * 24 * 3600 * 1000)

count = 0
for candle in client.iter_candles("BTC-EUR", Interval.MIN_1, since=start_ms):
    count += 1
    # Zpracování svíčky...

print(f"Staženo {count} svíček.")
```

!!! warning "Svíčka je slovník, ne objekt"
    `iter_candles()` vrací obyčejné slovníky. `print(candle())` skončí chybou
    `TypeError: 'dict' object is not callable` a `candle.close` vyhodí
    `AttributeError`. Pro výpis celého záznamu použijte `print(candle)`, pro
    jednu hodnotu `candle["close"]`. Všechny OHLCV hodnoty jsou **stringy**, aby
    se neztratila desetinná přesnost — před výpočty je převeďte na `Decimal`,
    nikoli na `float`.

#### Čtení jednotlivých polí

```python
from datetime import datetime, timezone

for candle in client.iter_candles("BTC-EUR", Interval.MIN_1, since=start_ms):
    opened = datetime.fromtimestamp(candle["start"] / 1000, tz=timezone.utc)
    print(
        f"{opened:%Y-%m-%d %H:%M} "
        f"O={candle['open']} H={candle['high']} "
        f"L={candle['low']} C={candle['close']} V={candle['volume']}"
    )
```

#### Omezení okna z obou stran
Parametrem `until` streamování ukončíte v pevném bodě místo v aktuálním čase:

```python
from datetime import datetime, time as dtime, timedelta, timezone

midnight = datetime.combine(
    datetime.now(timezone.utc).date(), dtime.min, tzinfo=timezone.utc
)
yesterday = midnight - timedelta(days=1)

candles = list(client.iter_candles(
    "BTC-EUR",
    Interval.MIN_1,
    since=int(yesterday.timestamp() * 1000),
    until=int(midnight.timestamp() * 1000),
))
print(f"{len(candles)} minutových svíček za {yesterday:%Y-%m-%d}")  # ~1441, 2 požadavky
```

Oba okraje držte relativní k *aktuálnímu času*, ne na pevných kalendářních
datech — fixní okno se s postupem času vysune mimo retenci a začne vracet
prázdno.

Oba nepovinné parametry se chovají takto:

| Argumenty | Chování |
| --- | --- |
| `since` + `until` | Prostránkuje celé okno, nic po `until` se nevrátí. |
| pouze `since` | Stránkuje od `since` až do aktuálního času. |
| žádný (nebo jen `until`) | **Bez stránkování** — jediný požadavek s nejnovější dávkou. |

#### Předčasné ukončení
Generátor je líný: další požadavek pošle teprve ve chvíli, kdy si řeknete o
další svíčku. Opuštění cyklu tedy zastaví i stahování.

```python
import itertools
from decimal import Decimal

# Nahlédnutí na prvních 10 svíček — jeden požadavek, ne celé stahování
head = itertools.islice(client.iter_candles("BTC-EUR", Interval.MIN_5, since=start_ms), 10)
for candle in head:
    print(candle["start"], candle["close"])

# Nebo ukončení podle podmínky
for candle in client.iter_candles("BTC-EUR", Interval.MIN_5, since=start_ms):
    if Decimal(candle["high"]) > Decimal("100000"):
        print("První průraz nad 100k v", candle["start"])
        break
```

#### Agregace bez držení všeho v paměti
Deset tisíc minutových svíček je hodně slovníků na jednou. Zpracovávejte je
průběžně:

```python
from decimal import Decimal

count = 0
high = Decimal("-Infinity")
low = Decimal("Infinity")
volume = Decimal(0)

for candle in client.iter_candles("BTC-EUR", Interval.MIN_1, since=start_ms):
    count += 1
    high = max(high, Decimal(candle["high"]))
    low = min(low, Decimal(candle["low"]))
    volume += Decimal(candle["volume"])

print(f"{count} svíček | rozsah za 7 dní {low}–{high} EUR | objem {volume} BTC")
```

#### Zápis přímo do CSV
`csv.DictWriter.writerows()` přijme generátor rovnou, soubor se tedy zapisuje
průběžně:

```python
import csv

with open("btc_eur_1m.csv", "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(
        fh, fieldnames=["start", "open", "high", "low", "close", "volume"]
    )
    writer.writeheader()
    writer.writerows(client.iter_candles("BTC-EUR", Interval.MIN_1, since=start_ms))
```

#### Načtení do pandas

```python
import pandas as pd

df = pd.DataFrame(client.iter_candles("BTC-EUR", Interval.HOUR_1, since=start_ms))
df["start"] = pd.to_datetime(df["start"], unit="ms", utc=True)
df = df.set_index("start").astype(float)

df["sma_24"] = df["close"].rolling(24).mean()
print(df.tail())
```

!!! note "Kolik je to požadavků a jak dlouho to trvá?"
    Jeden požadavek pokryje maximálně 1000 svíček a klient mezi požadavky čeká
    `request_delay` sekund (výchozí 0,85 s) a zároveň za vás opakuje odpovědi
    HTTP 429. 7 dní minutových dat je tedy 10 080 svíček ≈ 11 požadavků ≈ 10 s
    reálného času. Pro dlouhé historie zvolte hrubší interval, nebo si výsledek
    jednou uložte na disk a dál čtěte odtud.

!!! note "Generátor lze projít jen jednou"
    Po dokončení cyklu je iterátor vyčerpaný — druhý `for` nad stejným objektem
    nevrátí nic. Pokud potřebujete data projít vícekrát, převeďte je na seznam
    pomocí `list(...)`.
