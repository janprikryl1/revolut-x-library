"""Example 5: Fee Calculation and Client-Side Order Validation."""

from revolut_x import RevolutXClient, OrderSide, FeeCalculator, OrderPayloadBuilder


def main():
    # 1. Fee estimation (Maker 0.00% vs Taker 0.09%)
    maker = FeeCalculator.calculate(side=OrderSide.BUY, price="74000.00", is_maker=True, quote_size="100.00")
    taker = FeeCalculator.calculate(side=OrderSide.BUY, price="74000.00", is_maker=False, quote_size="100.00")

    print(f"Maker Fee (post_only): {maker.fee_amount} EUR ({maker.fee_rate_percent}%) -> Net ~{maker.net_received} BTC")
    print(f"Taker Fee (market):    {taker.fee_amount} EUR ({taker.fee_rate_percent}%) -> Net ~{taker.net_received} BTC")

    # 2. Client-side payload validation against live pair limits
    client = RevolutXClient()
    rules = client.get_pair("BTC-EUR")

    payload = OrderPayloadBuilder.build_limit_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        price="70000.00",
        quote_size="50.00",
        post_only=True,
    )
    is_valid, errors = OrderPayloadBuilder.validate_against_pair_rules(payload, rules)
    print(f"Validation against exchange rules: Passed = {is_valid} (Errors: {errors or 'None'})")


if __name__ == "__main__":
    main()
