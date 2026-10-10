"""Unit tests for MarketMixin in revolut_x.market."""

from __future__ import annotations
from typing import Any
from unittest.mock import MagicMock

from revolut_x.market import MarketMixin


INTERVAL_MIN = 1
INTERVAL_MS = INTERVAL_MIN * 60 * 1000


class FakeCandleClient(MarketMixin):
    """Client whose candle endpoint is backed by a synthetic, gap-free series.

    Mirrors the real API contract: the window is inclusive on both ends and a
    window spanning more than 1000 candles — or one where ``until`` is not
    strictly after ``since`` — is an error.
    """

    def __init__(self, first_start: int, count: int, *, missing: set[int] | None = None) -> None:
        self._http = MagicMock()
        self.series = [
            first_start + i * INTERVAL_MS
            for i in range(count)
            if i not in (missing or set())
        ]
        self.now = first_start + (count - 1) * INTERVAL_MS
        self.requests: list[tuple[int | None, int | None]] = []

    def get_candles(
        self,
        symbol: str,
        interval: Any = INTERVAL_MIN,
        *,
        since: int | None = None,
        until: int | None = None,
    ) -> list[dict[str, Any]]:
        self.requests.append((since, until))
        if since is not None and until is not None:
            assert until > since, (
                f"API rejects a window where until <= since (since={since}, until={until})"
            )
            assert (until - since) <= 999 * INTERVAL_MS, (
                f"API rejects a window of more than 1000 candles "
                f"({(until - since) // INTERVAL_MS + 1} requested)"
            )
        lo = since if since is not None else self.series[0]
        hi = until if until is not None else self.now
        return [{"start": s, "close": str(s)} for s in self.series if lo <= s <= hi][-1000:]


def _starts(candles: list[dict[str, Any]]) -> list[int]:
    return [c["start"] for c in candles]


def test_iter_candles_page_aligned_window_does_not_crash() -> None:
    """A window that is an exact multiple of the 1000-candle page size.

    Regression test: the window arithmetic used to leave exactly one candle
    over and then issue a final request with since == until, which the
    exchange rejects with HTTP 400 'Invalid interval'.
    """
    base = 1_700_000_000_000
    client = FakeCandleClient(base, 4000)
    since, until = base, base + 2000 * INTERVAL_MS

    got = _starts(list(client.iter_candles("BTC-EUR", INTERVAL_MIN, since=since, until=until)))

    expected = [base + i * INTERVAL_MS for i in range(2001)]
    assert got == expected
    assert len(got) == 2001
    # No request may degenerate to a zero-width window.
    assert all(u > s for s, u in client.requests if s is not None and u is not None)


def test_iter_candles_window_sizes_are_exact() -> None:
    """Every candle in the range is yielded exactly once, for several sizes."""
    base = 1_700_000_000_000
    for span in (1, 2, 998, 999, 1000, 1001, 1999, 2000, 3000):
        client = FakeCandleClient(base, 5000)
        until = base + span * INTERVAL_MS
        got = _starts(list(client.iter_candles("BTC-EUR", INTERVAL_MIN, since=base, until=until)))

        assert got == sorted(got), f"span={span}: not chronological"
        assert len(got) == len(set(got)), f"span={span}: duplicates yielded"
        assert len(got) == span + 1, f"span={span}: expected {span + 1} candles, got {len(got)}"
        assert got[0] == base and got[-1] == until, f"span={span}: range boundaries missing"


def test_iter_candles_never_yields_past_until() -> None:
    """The overshoot from a widened final window must be filtered out."""
    base = 1_700_000_000_000
    client = FakeCandleClient(base, 4000)
    until = base + 1000 * INTERVAL_MS

    got = _starts(list(client.iter_candles("BTC-EUR", INTERVAL_MIN, since=base, until=until)))

    assert max(got) == until
    assert all(s <= until for s in got)


def test_iter_candles_survives_gaps_in_the_series() -> None:
    """An illiquid pair with no trades for a stretch must not end iteration.

    A short page is not proof of the end of the data — it may just be a hole
    in the series, so pagination has to keep walking the requested range.
    """
    base = 1_700_000_000_000
    # Drop a contiguous block larger than a single page.
    missing = set(range(1200, 2500))
    client = FakeCandleClient(base, 4000, missing=missing)
    until = base + 3500 * INTERVAL_MS

    got = _starts(list(client.iter_candles("BTC-EUR", INTERVAL_MIN, since=base, until=until)))

    assert len(got) == 3501 - len(missing)
    # Data on the far side of the gap must still be reached.
    assert base + 3000 * INTERVAL_MS in got
    assert base + 1500 * INTERVAL_MS not in got


def test_iter_candles_without_since_makes_a_single_request() -> None:
    base = 1_700_000_000_000
    client = FakeCandleClient(base, 1500)

    got = list(client.iter_candles("BTC-EUR", INTERVAL_MIN))

    assert len(client.requests) == 1
    assert client.requests[0][0] is None
    assert len(got) == 1000


class DummyMarketClient(MarketMixin):
    def __init__(self) -> None:
        self._http = MagicMock()


def test_get_order_book_returns_levels_untouched() -> None:
    """Levels are passed through as dicts — price in 'p', quantity in 'q'."""
    client = DummyMarketClient()
    level = {
        "aid": "BTC", "anm": "Bitcoin", "s": "BUYI", "p": "73875.00", "pc": "EUR",
        "pn": "MONE", "q": "0.04966288", "qc": "BTC", "qn": "UNIT", "ve": "REVX",
        "no": "1", "ts": "CLOB", "pdt": "2026-10-10T14:01:14.705816Z",
    }
    payload = {"bids": [level], "asks": [dict(level, s="SELL", p="73895.00")]}
    client._http.request.return_value = (200, {"data": payload, "metadata": {"region": "EEA"}})

    book = client.get_order_book("BTC-EUR")

    assert book == payload
    assert book["bids"][0]["p"] == "73875.00"
    assert book["bids"][0]["q"] == "0.04966288"


def test_get_trades_limit_stays_within_the_api_bound() -> None:
    """The venue rejects limit > 100 with HTTP 400, so it must be clamped.

    Regression test: the default used to be 1900, which made every
    ``get_trades()`` / ``iter_trades()` call fail out of the box.
    """
    client = DummyMarketClient()
    client._http.request.return_value = (200, {"data": [], "metadata": {}})

    def sent_limit() -> int:
        return client._http.request.call_args.kwargs["params"]["limit"]

    client.get_trades("BTC-EUR")
    assert sent_limit() == 100, "default page size must be accepted by the API"

    client.get_trades("BTC-EUR", limit=1900)
    assert sent_limit() == 100

    client.get_trades("BTC-EUR", limit=0)
    assert sent_limit() == 1

    client.get_trades("BTC-EUR", limit=50)
    assert sent_limit() == 50


def test_get_ticker_matches_slash_and_dash_symbols() -> None:
    client = DummyMarketClient()
    btc = {"symbol": "BTC/EUR", "bid": "73875.00", "ask": "73895.00",
           "last_price": "73875", "volume_24h": "38.51"}
    client._http.request.return_value = (200, {"data": [{"symbol": "ETH/EUR"}, btc]})

    for requested in ("BTC-EUR", "BTC/EUR", "btc-eur"):
        client._http.request.return_value = (200, {"data": [{"symbol": "ETH/EUR"}, btc]})
        assert client.get_ticker(requested) == btc
