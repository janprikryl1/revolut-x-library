"""Example 1: Public Market Data (No API key required)."""

from revolut_x import RevolutXClient, Interval


def main():
    client = RevolutXClient()

    # 1. Market Ticker
    ticker = client.get_ticker("BTC-EUR")
    print(f"BTC-EUR: Last = {ticker['last_price']} EUR | Bid = {ticker['bid']} | Ask = {ticker['ask']}")

    # 2. Pair limits and rules
    pair = client.get_pair("BTC-EUR")
    print(f"Limits:  Min = {pair['min_order_size_quote']} EUR / {pair['min_order_size']} BTC")

    # 3. Order Book snapshot — levels are dicts: price in 'p', quantity in 'q'
    book = client.get_order_book("BTC-EUR")
    top_ask, top_bid = book["asks"][0], book["bids"][0]
    print(f"Top Ask: {top_ask['p']} EUR x {top_ask['q']} BTC | "
          f"Top Bid: {top_bid['p']} EUR x {top_bid['q']} BTC")

    # 4. Candlesticks (OHLCV)
    candles = client.get_candles("BTC-EUR", interval=Interval.HOUR_1)
    if candles:
        latest = candles[-1]
        print(f"Latest 1h Candle: Open = {latest['open']}, Close = {latest['close']}, Vol = {latest['volume']}")


if __name__ == "__main__":
    main()
