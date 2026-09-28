"""Example 4: Order Placement and Cancellation (Requires API credentials)."""

import os
from pathlib import Path
from dotenv import load_dotenv
from revolut_x import RevolutXClient, OrderSide

# Load .env
for candidate in (Path(".env"), Path("../.env"), Path("../../.env")):
    if candidate.exists():
        load_dotenv(candidate)
        break


def main():
    api_key = os.getenv("REVOLUT_API_KEY")
    key_path = os.getenv("REVOLUT_PRIVATE_KEY_PATH", "keys/private.pem")

    client = RevolutXClient(api_key=api_key, private_key_path=key_path)

    # 1. Place a safe Maker limit buy order 50% below market (0.00% fee)
    ticker = client.get_ticker("BTC-EUR")
    safe_price = str(round(float(ticker["last_price"]) * 0.5, 2))

    order = client.place_limit_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        price=safe_price,
        quote_size="1.00",
        post_only=True,
    )
    order_id = order["venue_order_id"]
    print(f"Placed safe order: {order_id} @ {safe_price} EUR (State: {order['state']})")

    # 2. Inspect order details from exchange
    detail = client.get_order(order_id)
    print(f"Order status on exchange: {detail['status']} | Fee: {detail['total_fee']} EUR")

    # 3. Cancel the order
    client.cancel_order(order_id)
    print(f"Order {order_id} canceled successfully.")


if __name__ == "__main__":
    main()
