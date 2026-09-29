from __future__ import annotations
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from revolut_x.types import OrderSide, OrderType, TimeInForce
from revolut_x.exceptions import OrderValidationError


def normalize_symbol(symbol: str) -> str:
    """Normalizes the trading symbol for the Revolut X API.

    Accepts formats such as 'BTC/EUR', 'BTC-EUR', 'btc-eur', 'btceur', 'BTCEUR'.
    Returns the normalized symbol with a dash separator (e.g. 'BTC-EUR').

    Args:
        symbol: The trading symbol to normalize.

    Returns:
        str: The normalized symbol.

    Example:
        >>> normalize_symbol('BTC/EUR')
        'BTC-EUR'
        >>> normalize_symbol('btceur')
        'BTC-EUR'
    """
    clean = symbol.replace("/", "").replace("-", "").upper()
    for quote in ("USDC", "EUR", "USD", "GBP", "CZK"):
        if clean.endswith(quote):
            base = clean[: -len(quote)]
            if base:
                return f"{base}-{quote}"
    return symbol.replace("/", "-").upper()


class OrderPayloadBuilder:
    """Builder and validator for Revolut X API order payloads."""

    @staticmethod
    def _format_decimal(val: Any) -> str:
        """Converts a number, float, or Decimal to a string representation.

        Args:
            val: The numerical value to convert.

        Returns:
            str: The string representation of the decimal value.

        Raises:
            OrderValidationError: If the value is an invalid number or unsupported type.

        Example:
            >>> OrderPayloadBuilder._format_decimal(50.5)
            '50.5'
        """
        if isinstance(val, str):
            try:
                d = Decimal(val)
                return str(d)
            except InvalidOperation:
                raise OrderValidationError(f"Invalid numerical value: {val}")
        elif isinstance(val, (int, float, Decimal)):
            return str(Decimal(str(val)))
        else:
            raise OrderValidationError(f"Unexpected numerical value type: {type(val)}")

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """Normalizes the trading symbol for the Revolut X API."""
        return normalize_symbol(symbol)

    normalize_symbol = staticmethod(normalize_symbol)

    @classmethod
    def build_market_order(
        cls,
        symbol: str,
        side: OrderSide,
        *,
        base_size: Any | None = None,
        quote_size: Any | None = None,
        client_order_id: str | None = None
    ) -> dict[str, Any]:
        """Builds a payload for a Market Order.

        Args:
            symbol: The trading symbol (e.g., 'BTC-EUR').
            side: The side of the order (BUY or SELL).
            base_size: The amount of the base currency (e.g., BTC) to buy/sell.
            quote_size: The amount of the quote currency (e.g., EUR) to buy/sell.
            client_order_id: A unique client order ID. A UUID will be generated if not provided.

        Returns:
            dict[str, Any]: The constructed JSON payload for the Revolut X API.

        Raises:
            OrderValidationError: If exactly one of base_size or quote_size is not provided.

        Example:
            >>> OrderPayloadBuilder.build_market_order('BTC-EUR', OrderSide.BUY, quote_size='50.00')
        """
        if (base_size is None and quote_size is None) or (base_size is not None and quote_size is not None):
            raise OrderValidationError("You must specify exactly one field: either 'base_size' or 'quote_size'.")

        market_conf: dict[str, str] = {}
        if base_size is not None:
            market_conf["base_size"] = cls._format_decimal(base_size)
        else:
            market_conf["quote_size"] = cls._format_decimal(quote_size)

        return {
            "client_order_id": client_order_id or str(uuid.uuid4()),
            "symbol": cls._normalize_symbol(symbol),
            "side": side.value if isinstance(side, OrderSide) else str(side).lower(),
            "order_configuration": {
                "market": market_conf
            }
        }

    @classmethod
    def build_limit_order(
        cls,
        symbol: str,
        side: OrderSide,
        price: Any,
        *,
        base_size: Any | None = None,
        quote_size: Any | None = None,
        post_only: bool = False,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
        client_order_id: str | None = None
    ) -> dict[str, Any]:
        """Builds a payload for a Limit Order.

        Args:
            symbol: The trading symbol (e.g., 'BTC-EUR').
            side: The side of the order (BUY or SELL).
            price: The limit price in quote currency per 1 base currency unit.
            base_size: The amount of the base currency (e.g., BTC) to buy/sell.
            quote_size: The amount of the quote currency (e.g., EUR) to buy/sell.
            post_only: If True, ensures the order is entered as a MAKER order.
            time_in_force: The time in force for the order (e.g., 'gtc' or 'ioc').
            client_order_id: A unique client order ID. A UUID will be generated if not provided.

        Returns:
            dict[str, Any]: The constructed JSON payload for the Revolut X API.

        Raises:
            OrderValidationError: If exactly one of base_size or quote_size is not provided.

        Example:
            >>> OrderPayloadBuilder.build_limit_order('BTC-EUR', OrderSide.SELL, '90000.00', base_size='0.1')
        """
        if (base_size is None and quote_size is None) or (base_size is not None and quote_size is not None):
            raise OrderValidationError("You must specify exactly one field: either 'base_size' or 'quote_size'.")

        execution_instructions: list[str] = ["post_only"] if post_only else ["allow_taker"]

        tif_val = time_in_force.value if isinstance(time_in_force, TimeInForce) else str(time_in_force).lower()

        limit_conf: dict[str, Any] = {
            "price": cls._format_decimal(price),
            "time_in_force": tif_val,
            "execution_instructions": execution_instructions
        }

        if base_size is not None:
            limit_conf["base_size"] = cls._format_decimal(base_size)
        else:
            limit_conf["quote_size"] = cls._format_decimal(quote_size)

        return {
            "client_order_id": client_order_id or str(uuid.uuid4()),
            "symbol": cls._normalize_symbol(symbol),
            "side": side.value if isinstance(side, OrderSide) else str(side).lower(),
            "order_configuration": {
                "limit": limit_conf
            }
        }

    @classmethod
    def build_order(
        cls,
        symbol: str,
        side: OrderSide | str,
        order_type: OrderType | str = OrderType.MARKET,
        *,
        price: Any | None = None,
        base_size: Any | None = None,
        quote_size: Any | None = None,
        post_only: bool = False,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Builds a payload for either a Market or Limit Order based on order_type.

        Args:
            symbol: The trading symbol (e.g., 'BTC-EUR').
            side: The side of the order (BUY or SELL).
            order_type: OrderType.MARKET ('market') or OrderType.LIMIT ('limit').
            price: Required for limit orders. Must be None for market orders.
            base_size: The amount of the base currency (e.g., BTC) to buy/sell.
            quote_size: The amount of the quote currency (e.g., EUR) to buy/sell.
            post_only: If True, ensures the order is entered as a MAKER order (limit only).
            time_in_force: The time in force policy (limit only).
            client_order_id: Optional client-side UUID for idempotency.

        Returns:
            dict[str, Any]: The constructed JSON payload for the Revolut X API.

        Raises:
            OrderValidationError: If parameters are invalid for the given order_type.

        Example:
            >>> OrderPayloadBuilder.build_order('BTC-EUR', OrderSide.BUY, order_type=OrderType.MARKET, quote_size='50.00')
        """
        if isinstance(order_type, str):
            try:
                order_type = OrderType(order_type.lower())
            except ValueError:
                raise OrderValidationError(f"Invalid order_type: '{order_type}'. Expected 'market' or 'limit'.")

        if isinstance(side, str):
            try:
                side = OrderSide(side.lower())
            except ValueError:
                raise OrderValidationError(f"Invalid side: '{side}'. Expected 'buy' or 'sell'.")

        if order_type == OrderType.MARKET:
            if price is not None:
                raise OrderValidationError("Parameter 'price' is not supported for market orders.")
            if post_only:
                raise OrderValidationError("Parameter 'post_only' is not supported for market orders.")
            return cls.build_market_order(
                symbol=symbol,
                side=side,
                base_size=base_size,
                quote_size=quote_size,
                client_order_id=client_order_id,
            )
        elif order_type == OrderType.LIMIT:
            if price is None:
                raise OrderValidationError("Parameter 'price' is required for limit orders.")
            return cls.build_limit_order(
                symbol=symbol,
                side=side,
                price=price,
                base_size=base_size,
                quote_size=quote_size,
                post_only=post_only,
                time_in_force=time_in_force,
                client_order_id=client_order_id,
            )
        else:
            raise OrderValidationError(f"Unsupported order_type: {order_type}")

    @classmethod
    def validate_against_pair_rules(
        cls,
        payload: dict[str, Any],
        pair_rules: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validates the constructed payload against the exchange's trading pair rules.

        Args:
            payload: The order payload to validate.
            pair_rules: The trading rules for the specific asset pair.

        Returns:
            tuple[bool, list[str]]: A tuple containing a boolean indicating if the payload is valid,
                and a list of error messages (if any).

        Example:
            >>> valid, errors = OrderPayloadBuilder.validate_against_pair_rules(payload, rules)
        """
        errors: list[str] = []
        conf = payload.get("order_configuration", {})

        is_market = "market" in conf
        is_limit = "limit" in conf
        order_data = conf.get("market") if is_market else conf.get("limit", {})

        base_size = order_data.get("base_size")
        quote_size = order_data.get("quote_size")
        price = order_data.get("price")

        min_base = Decimal(pair_rules.get("min_order_size", "0.00000001"))
        max_base = Decimal(pair_rules.get("max_order_size", "1000000"))
        min_quote = Decimal(pair_rules.get("min_order_size_quote", "0.1"))
        max_quote = Decimal(pair_rules.get("max_order_size_quote", "1000000"))

        if base_size:
            b_dec = Decimal(base_size)
            if b_dec < min_base:
                errors.append(f"base_size ({b_dec}) is less than the minimum ({min_base})")
            if b_dec > max_base:
                errors.append(f"base_size ({b_dec}) is greater than the maximum ({max_base})")

        if quote_size:
            q_dec = Decimal(quote_size)
            if q_dec < min_quote:
                errors.append(f"quote_size ({q_dec}) is less than the minimum ({min_quote})")
            if q_dec > max_quote:
                errors.append(f"quote_size ({q_dec}) is greater than the maximum ({max_quote})")

        if is_limit and not price:
            errors.append("Limit order is missing the 'price' field!")

        return len(errors) == 0, errors

    @classmethod
    def build_maker_order(
        cls,
        symbol: str,
        side: OrderSide | str,
        price: Any,
        *,
        base_size: Any | None = None,
        quote_size: Any | None = None,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Builds a payload for a guaranteed zero-fee Maker Order (Limit with post_only=True).

        Args:
            symbol: The trading symbol (e.g. 'BTC-EUR').
            side: OrderSide.BUY or OrderSide.SELL.
            price: Limit price in quote currency per 1 base unit.
            base_size: Amount in base currency (e.g. BTC).
            quote_size: Amount in quote currency (e.g. EUR).
            time_in_force: Time in force (default: GTC).
            client_order_id: Optional client UUID.

        Returns:
            dict[str, Any]: JSON payload ready for the Revolut X API.
        """
        return cls.build_limit_order(
            symbol=symbol,
            side=side,
            price=price,
            base_size=base_size,
            quote_size=quote_size,
            post_only=True,
            time_in_force=time_in_force,
            client_order_id=client_order_id,
        )


def calculate_maker_price(
    side: OrderSide | str,
    *,
    best_bid: Any | None = None,
    best_ask: Any | None = None,
    last_price: Any | None = None,
    offset: Any = Decimal("0.10"),
    tick_size: Any = Decimal("0.01"),
) -> Decimal:
    """Calculates an optimal limit price to guarantee entry into the order book as a Maker (0.00% fee).

    For BUY orders:
        price = (best_bid or last_price) - offset
    For SELL orders:
        price = (best_ask or last_price) + offset

    Args:
        side: OrderSide.BUY / OrderSide.SELL or string ('buy' / 'sell').
        best_bid: Current best bid price (highest buyer in book).
        best_ask: Current best ask price (lowest seller in book).
        last_price: Fallback price if best bid/ask is not available.
        offset: Safety offset in quote currency (default: 0.10 EUR/USD).
        tick_size: Minimum price increment for quantisation (default: 0.01).

    Returns:
        Decimal: The quantised target price.

    Raises:
        OrderValidationError: If side is invalid or no valid reference price can be determined.

    Example:
        >>> calculate_maker_price(OrderSide.BUY, best_bid="80000.00", offset="0.10")
        Decimal('79999.90')
        >>> calculate_maker_price(OrderSide.SELL, best_ask="80000.50", offset="0.10")
        Decimal('80000.60')
    """
    if isinstance(side, str):
        try:
            side_enum = OrderSide(side.lower())
        except ValueError:
            raise OrderValidationError(f"Invalid side: '{side}'. Expected 'buy' or 'sell'.")
    elif isinstance(side, OrderSide):
        side_enum = side
    else:
        raise OrderValidationError(f"Invalid side type: {type(side)}")

    offset_dec = Decimal(str(offset))
    tick_dec = Decimal(str(tick_size))

    if side_enum == OrderSide.BUY:
        ref = best_bid if best_bid is not None else last_price
        if ref is None:
            raise OrderValidationError("Cannot calculate Maker BUY price: neither 'best_bid' nor 'last_price' provided.")
        raw_price = Decimal(str(ref)) - offset_dec
    else:
        ref = best_ask if best_ask is not None else last_price
        if ref is None:
            raise OrderValidationError("Cannot calculate Maker SELL price: neither 'best_ask' nor 'last_price' provided.")
        raw_price = Decimal(str(ref)) + offset_dec

    # Quantize to tick size
    return raw_price.quantize(tick_dec, rounding=ROUND_HALF_UP)


@dataclass
class FeeEstimate:
    """Estimated fee calculation result for an order."""
    side: str
    order_type: str
    is_maker: bool
    fee_rate_percent: Decimal
    trade_value_eur: Decimal
    estimated_base_qty: Decimal
    price: Decimal
    fee_amount: Decimal
    fee_currency: str
    net_received: Decimal
    net_received_currency: str
    explanation: str


class FeeCalculator:
    """Calculator for order fees on Revolut X."""

    MAKER_FEE_RATE = Decimal("0.0000")  # 0.00%
    TAKER_FEE_RATE = Decimal("0.0009")  # 0.09%

    @classmethod
    def calculate(
        cls,
        side: OrderSide,
        price: Any,
        is_maker: bool,
        *,
        base_size: Any | None = None,
        quote_size: Any | None = None
    ) -> FeeEstimate:
        """Calculates exact fees for a specified trade.

        Args:
            side: BUY or SELL.
            price: The execution price in quote currency per 1 base currency unit.
            is_maker: True if the order is executed as a maker (0.00% fee), False for taker (0.09% fee).
            base_size: The amount of the base currency (e.g., BTC) if provided.
            quote_size: The amount of the quote currency (e.g., EUR) if provided.

        Returns:
            FeeEstimate: An object containing detailed fee estimates.

        Raises:
            OrderValidationError: If neither base_size nor quote_size is provided.

        Example:
            >>> FeeCalculator.calculate(OrderSide.BUY, '90000', is_maker=False, quote_size='1000')
        """
        price_dec = Decimal(str(price))
        rate = cls.MAKER_FEE_RATE if is_maker else cls.TAKER_FEE_RATE
        rate_pct = rate * Decimal("100")

        if quote_size is not None:
            value_eur = Decimal(str(quote_size))
            qty_btc = (value_eur / price_dec).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
        elif base_size is not None:
            qty_btc = Decimal(str(base_size))
            value_eur = (qty_btc * price_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            raise OrderValidationError("You must specify either 'base_size' or 'quote_size'.")

        fee_eur = (value_eur * rate).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        side_val = side.value if isinstance(side, OrderSide) else str(side).lower()

        if side_val == "buy":
            fee_currency = "EUR"
            net_received = qty_btc
            net_currency = "BTC"
            explanation = (
                f"Buy {net_received} BTC for {value_eur} EUR at price {price_dec}.\n"
                f"- Execution type: {'MAKER' if is_maker else 'TAKER'}\n"
                f"- Fee rate: {rate_pct:.2f} %\n"
                f"- Fee amount: {fee_eur:.4f} EUR\n"
                f"- Net received approx: {net_received:.8f} BTC"
            )
        else:
            fee_currency = "EUR"
            net_received = (value_eur - fee_eur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            net_currency = "EUR"
            explanation = (
                f"Sell {qty_btc} BTC at price {price_dec} (Gross value: {value_eur} EUR).\n"
                f"- Execution type: {'MAKER' if is_maker else 'TAKER'}\n"
                f"- Fee rate: {rate_pct:.2f} %\n"
                f"- Fee amount: {fee_eur:.4f} EUR\n"
                f"- Net received: {net_received:.2f} EUR"
            )

        return FeeEstimate(
            side=side_val,
            order_type="limit" if is_maker else "market/immediate-limit",
            is_maker=is_maker,
            fee_rate_percent=rate_pct,
            trade_value_eur=value_eur,
            estimated_base_qty=qty_btc,
            price=price_dec,
            fee_amount=fee_eur,
            fee_currency=fee_currency,
            net_received=net_received,
            net_received_currency=net_currency,
            explanation=explanation
        )


# Module-level convenience functions
build_order = OrderPayloadBuilder.build_order
build_market_order = OrderPayloadBuilder.build_market_order
build_limit_order = OrderPayloadBuilder.build_limit_order
build_maker_order = OrderPayloadBuilder.build_maker_order
validate_against_pair_rules = OrderPayloadBuilder.validate_against_pair_rules

__all__ = [
    "OrderPayloadBuilder",
    "FeeEstimate",
    "FeeCalculator",
    "normalize_symbol",
    "calculate_maker_price",
    "build_order",
    "build_market_order",
    "build_limit_order",
    "build_maker_order",
    "validate_against_pair_rules",
]
