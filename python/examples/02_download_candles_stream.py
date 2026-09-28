"""Example 2: Historical Candlestick Stream (Automatic Pagination)."""

import time
from revolut_x import RevolutXClient, Interval


def main():
    client = RevolutXClient()

    # Stream the last 2 days of 1-minute candles (2880 candles > 1000 single-batch limit)
    start_ms = int(time.time() * 1000) - (2 * 24 * 3600 * 1000)

    count = 0
    for candle in client.iter_candles("BTC-EUR", interval=Interval.MIN_1, since=start_ms):
        count += 1
        if count <= 3:
            print(f"Candle #{count}: Time = {candle['start']} | Open = {candle['open']} | Close = {candle['close']}")

    print(f"Successfully streamed {count} candles seamlessly.")


if __name__ == "__main__":
    main()
