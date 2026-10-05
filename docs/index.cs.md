# Revolut X Python
<em>Python SDK pro REST API kryptoměnové burzy Revolut X (v1.0).</em>

---

!!! tip "Vícejazyčný ekosystém"
    Hledáte **PHP SDK**? Podívejte se na [Revolut X PHP Dokumentaci](https://janprikryl1.github.io/revolut-x-php/) nebo [PHP GitHub Repozitář](https://github.com/janprikryl1/revolut-x-php).

---

- **Podpora Revolut X API v1.0** — Cílí na oficiální Revolut X REST API `1.0` s konfigurovatelnou verzí.
- **Ed25519 Autentizace** — Průmyslový standard pro kryptografické podepisování soukromých endpointů.
- **Komplexní tržní data** — Živá kniha objednávek (order book), tickery v reálném čase, pravidla měnových párů, OHLCV svíčky i stream veřejných obchodů.
- **Automatizované streamovací iterátory** — `iter_candles()` a `iter_trades()` transparentně řeší kurzorové stránkování i rate-limiting okna.
- **Podpora obchodování bez poplatků** — Prvotřídní podpora pro `post_only` Maker příkazy (0.00% poplatek).
- **Vestavěné pomocné nástroje** — `FeeCalculator` a `OrderPayloadBuilder` poskytují offline validaci pravidel před odesláním a kalkulaci poplatků.
- **100% typové anotace** — Využívá Python `TypedDict`, `Enum` a moderní typové anotace pro okamžité našeptávání ve VS Code i PyCharmu.
- **Strukturované výjimky** — Hierarchické zpracování chyb (`AuthenticationError`, `RateLimitError`, `ApiError`, `NetworkError`).
- **Skill pro AI agenty** — Přibalený skill pro AI asistenty (Google Antigravity, Claude, Cursor) pro automatizaci burzovních úloh. Více v [Integrace AI agentů](guide/ai_agents.md).

---

## Instalace a stažení

### Instalace balíčku
```bash
# Standardní instalace z PyPI:
pip install revolut-x-python

# Nebo z TestPyPI:
pip install -i https://test.pypi.org/simple/ revolut-x-python

# Přímá instalace z GitHubu:
pip install "git+https://github.com/janprikryl1/revolut-x-python.git#subdirectory=python"
```

### Zdrojový kód a odkazy
- **GitHub Repozitář**: [github.com/janprikryl1/revolut-x-python](https://github.com/janprikryl1/revolut-x-python)
- **PHP SDK**: Samostatná knihovna pro PHP je k dispozici na [github.com/janprikryl1/revolut-x-php](https://github.com/janprikryl1/revolut-x-php).

---

## Rychlá ukázka kódu

```python
from revolut_x import RevolutXClient, OrderSide, OrderType, Interval

# 1. Veřejná tržní data (bez nutnosti API klíče)
client = RevolutXClient()
ticker = client.get_ticker("BTC-EUR")
print(f"BTC Cena: {ticker['last_price']} EUR")

# 2. Autentizované obchodování s 0% poplatkem
client = RevolutXClient(
    api_key="your_api_key_here",
    private_key_path="keys/private.pem",
)

order = client.place_maker_order(
    symbol="BTC-EUR",
    side=OrderSide.BUY,
    quote_size="50.00",
    offset="0.10",
)
print(f"ID Objednávky: {order['venue_order_id']}")
```

---

## Reference

Tato knihovna vznikla jako součást **diplomové práce** na **VŠB – Technické univerzitě Ostrava** (Fakulta elektrotechniky a informatiky).

- VŠB – Technická univerzita Ostrava, fakulta elektrotechniky a informatiky
- **Typ práce**: Diplomová práce / Master's Thesis
- **Autor**: Bc. Jan Přikryl
