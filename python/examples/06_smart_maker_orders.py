"""Example 6: Smart Zero-Fee Maker Orders with Dynamic Offset Pricing."""

import os
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv
from revolut_x import (
    RevolutXClient,
    OrderSide,
    calculate_maker_price,
    FeeCalculator,
)

# Load .env credentials if available
for candidate in (Path(".env"), Path("../.env"), Path("../../.env")):
    if candidate.exists():
        load_dotenv(candidate)
        break


def main():
    # Public helper usage (no credentials needed)
    print("--- 1. Pure Price Calculation (Offline/Public) ---")
    best_bid = Decimal("84500.00")
    best_ask = Decimal("84501.20")
    offset = Decimal("0.10")

    buy_maker_price = calculate_maker_price(
        side=OrderSide.BUY,
        best_bid=best_bid,
        offset=offset,
    )
    sell_maker_price = calculate_maker_price(
        side=OrderSide.SELL,
        best_ask=best_ask,
        offset=offset,
    )
    print(f"Market Best Bid: {best_bid} EUR  -> Optimal BUY Maker Price:  {buy_maker_price} EUR (0.00% fee)")
    print(f"Market Best Ask: {best_ask} EUR  -> Optimal SELL Maker Price: {sell_maker_price} EUR (0.00% fee)")

    # Fee comparison
    fee_maker = FeeCalculator.calculate(OrderSide.BUY, buy_maker_price, is_maker=True, quote_size="100.00")
    fee_taker = FeeCalculator.calculate(OrderSide.BUY, best_ask, is_maker=False, quote_size="100.00")
    print(f"\nFee comparison for 100 EUR trade:")
    print(f"  Maker (0.00%): {fee_maker.fee_amount} EUR fee -> Receives ~{fee_maker.net_received} BTC")
    print(f"  Taker (0.09%): {fee_taker.fee_amount} EUR fee -> Receives ~{fee_taker.net_received} BTC")

    # Authenticated client usage (if credentials configured)
    api_key = os.getenv("REVOLUT_API_KEY")
    key_path = os.getenv("REVOLUT_PRIVATE_KEY_PATH", "keys/private.pem")

    if not api_key or not Path(key_path).exists():
        print("\n[NOTE] Set REVOLUT_API_KEY and REVOLUT_PRIVATE_KEY_PATH in .env to submit live orders.")
        return

    client = RevolutXClient(api_key=api_key, private_key_path=key_path)

    print("\n--- 2. Live Dynamic Maker Order via Client ---")
    # client.place_maker_order automatically:
    # 1. Queries live ticker (best bid/ask)
    # 2. Applies the offset (default 0.10 EUR)
    # 3. Submits post_only limit order with guaranteed 0.00% Maker fee
    try:
        order = client.place_maker_order(
            symbol="BTC-EUR",
            side=OrderSide.BUY,
            quote_size="10.00",
            offset=Decimal("0.10"),
        )
        print(f"Order successfully placed: ID={order.get('venue_order_id')}, State={order.get('state')}")
    except Exception as e:
        print(f"Order execution result/error: {e}")


if __name__ == "__main__":
    main()
