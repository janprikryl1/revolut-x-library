"""Unit tests for the revolut_x.helpers module."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

import pytest

from revolut_x.exceptions import OrderValidationError, RevolutXError
from revolut_x.helpers import (
    FeeCalculator,
    FeeEstimate,
    OrderPayloadBuilder,
    build_limit_order,
    build_market_order,
    build_order,
    normalize_symbol,
    validate_against_pair_rules,
)
from revolut_x.types import OrderSide, OrderType, TimeInForce


def test_build_market_order_with_quote_size() -> None:
    """Verify market order payload structure when quote_size is provided."""

    payload = build_market_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        quote_size="50.00",
    )

    assert payload["symbol"] == "BTC-EUR"
    assert payload["side"] == OrderSide.BUY.value
    assert "market" in payload["order_configuration"]

    market_conf = payload["order_configuration"]["market"]
    assert market_conf["quote_size"] == "50.00"
    assert "base_size" not in market_conf

    # Verify OrderPayloadBuilder produces identical payload configuration
    payload_builder = OrderPayloadBuilder.build_market_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        quote_size="50.00",
    )
    assert payload_builder["order_configuration"] == payload["order_configuration"]

    # Verify client_order_id was auto-generated
    assert "client_order_id" in payload
    assert isinstance(payload["client_order_id"], str)
    assert len(payload["client_order_id"]) > 0


def test_build_market_order_with_base_size() -> None:
    """Verify market order payload structure when base_size is provided."""
    custom_order_id = "custom-order-uuid-987"
    payload = build_market_order(
        symbol="BTC/EUR",
        side=OrderSide.SELL,
        base_size="0.005",
        client_order_id=custom_order_id,
    )

    assert payload["client_order_id"] == custom_order_id
    assert payload["symbol"] == "BTC-EUR"
    assert payload["side"] == OrderSide.SELL.value
    assert "market" in payload["order_configuration"]

    market_conf = payload["order_configuration"]["market"]
    assert market_conf["base_size"] == "0.005"
    assert "quote_size" not in market_conf


def test_build_market_order_missing_both_sizes() -> None:
    """Verify ValueError / OrderValidationError is raised when neither size is provided."""
    with pytest.raises(ValueError) as exc_info:
        build_market_order(symbol="BTC-EUR", side=OrderSide.BUY)

    assert "either 'base_size' or 'quote_size'" in str(exc_info.value)
    assert isinstance(exc_info.value, OrderValidationError)
    assert isinstance(exc_info.value, RevolutXError)


def test_build_market_order_both_sizes_given() -> None:
    """Verify ValueError / OrderValidationError is raised when both sizes are provided."""
    with pytest.raises(ValueError) as exc_info:
        build_market_order(
            symbol="BTC-EUR",
            side=OrderSide.BUY,
            base_size="0.01",
            quote_size="500.00",
        )

    assert "either 'base_size' or 'quote_size'" in str(exc_info.value)
    assert isinstance(exc_info.value, OrderValidationError)
    assert isinstance(exc_info.value, RevolutXError)


def test_build_limit_order_post_only() -> None:
    """Verify limit order payload with post_only sets execution_instructions correctly."""
    # When post_only=True
    payload_post = build_limit_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        price="50000.00",
        base_size="0.1",
        post_only=True,
        time_in_force=TimeInForce.GTC,
    )

    limit_conf = payload_post["order_configuration"]["limit"]
    assert "post_only" in limit_conf["execution_instructions"]
    assert "allow_taker" not in limit_conf["execution_instructions"]
    assert limit_conf["price"] == "50000.00"
    assert limit_conf["base_size"] == "0.1"
    assert limit_conf["time_in_force"] == TimeInForce.GTC.value

    # When post_only=False
    payload_taker = build_limit_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        price="50000.00",
        base_size="0.1",
        post_only=False,
        time_in_force=TimeInForce.IOC,
    )
    limit_conf_taker = payload_taker["order_configuration"]["limit"]
    assert "allow_taker" in limit_conf_taker["execution_instructions"]
    assert "post_only" not in limit_conf_taker["execution_instructions"]
    assert limit_conf_taker["time_in_force"] == TimeInForce.IOC.value


def test_build_order_market() -> None:
    """Verify build_order routes to market order when order_type='market'."""
    payload = build_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quote_size="75.00",
    )
    assert payload["symbol"] == "BTC-EUR"
    assert payload["side"] == "buy"
    assert "market" in payload["order_configuration"]
    assert payload["order_configuration"]["market"]["quote_size"] == "75.00"

    # String order_type
    payload_str = build_order(
        symbol="BTC-EUR",
        side="buy",
        order_type="market",
        quote_size="75.00",
    )
    assert payload_str["order_configuration"] == payload["order_configuration"]

    # Market order with price should raise error
    with pytest.raises(OrderValidationError) as exc_info:
        build_order(
            symbol="BTC-EUR",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            price="50000.00",
            quote_size="75.00",
        )
    assert "Parameter 'price' is not supported for market orders" in str(exc_info.value)


def test_build_order_limit() -> None:
    """Verify build_order routes to limit order when order_type='limit'."""
    payload = build_order(
        symbol="BTC-EUR",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        price="95000.00",
        base_size="0.05",
        post_only=True,
    )
    assert payload["symbol"] == "BTC-EUR"
    assert payload["side"] == "sell"
    assert "limit" in payload["order_configuration"]
    limit_conf = payload["order_configuration"]["limit"]
    assert limit_conf["price"] == "95000.00"
    assert limit_conf["base_size"] == "0.05"
    assert "post_only" in limit_conf["execution_instructions"]

    # Limit order without price should raise error
    with pytest.raises(OrderValidationError) as exc_info:
        build_order(
            symbol="BTC-EUR",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            base_size="0.05",
        )
    assert "Parameter 'price' is required for limit orders" in str(exc_info.value)


def test_build_order_invalid_type() -> None:
    """Verify invalid order_type raises OrderValidationError."""
    with pytest.raises(OrderValidationError) as exc_info:
        build_order(
            symbol="BTC-EUR",
            side=OrderSide.BUY,
            order_type="stop_limit",
            base_size="0.05",
        )
    assert "Invalid order_type" in str(exc_info.value)


def test_normalize_symbol() -> None:
    """Verify symbol normalization with slash and unseparated lowercase pair formats."""
    assert normalize_symbol("BTC/EUR") == "BTC-EUR"
    assert normalize_symbol("btceur") == "BTC-EUR"
    assert normalize_symbol("BTC-EUR") == "BTC-EUR"
    assert normalize_symbol("btc-eur") == "BTC-EUR"
    assert normalize_symbol("ETH/USDC") == "ETH-USDC"
    assert normalize_symbol("ethusdc") == "ETH-USDC"


def test_validate_against_pair_rules_valid() -> None:
    """Verify valid order payload returns (True, []) against pair configuration."""
    pair_rules: Dict[str, Any] = {
        "min_order_size": "0.0001",
        "max_order_size": "100.0",
        "min_order_size_quote": "5.0",
        "max_order_size_quote": "100000.0",
    }
    payload = build_market_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        quote_size="50.0",
    )

    is_valid, errors = validate_against_pair_rules(payload, pair_rules)
    assert is_valid is True
    assert errors == []


def test_validate_against_pair_rules_invalid_min() -> None:
    """Verify invalid order below minimum returns (False, [error_msg])."""
    pair_rules: Dict[str, Any] = {
        "min_order_size": "0.001",
        "max_order_size": "10.0",
        "min_order_size_quote": "10.0",
        "max_order_size_quote": "50000.0",
    }

    # Quote size too small (5.0 < 10.0)
    payload_quote = build_market_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        quote_size="5.0",
    )
    is_valid_q, errors_q = validate_against_pair_rules(payload_quote, pair_rules)
    assert is_valid_q is False
    assert len(errors_q) == 1
    assert "quote_size (5.0) is less than the minimum (10.0)" in errors_q[0]

    # Base size too small (0.0001 < 0.001)
    payload_base = build_market_order(
        symbol="BTC-EUR",
        side=OrderSide.SELL,
        base_size="0.0001",
    )
    is_valid_b, errors_b = validate_against_pair_rules(payload_base, pair_rules)
    assert is_valid_b is False
    assert len(errors_b) == 1
    assert "base_size (0.0001) is less than the minimum (0.001)" in errors_b[0]


def test_fee_calculator_maker() -> None:
    """Verify maker fee rate is 0.00% and calculated fee amount is 0."""
    estimate: FeeEstimate = FeeCalculator.calculate(
        side=OrderSide.BUY,
        price="50000.00",
        is_maker=True,
        quote_size="1000.00",
    )

    assert estimate.is_maker is True
    assert estimate.fee_rate_percent == Decimal("0.00")
    assert estimate.fee_amount == Decimal("0.0000")
    assert estimate.order_type == OrderType.LIMIT.value
    assert estimate.fee_currency == "EUR"


def test_fee_calculator_taker() -> None:
    """Verify taker fee rate is 0.09% and calculated fee amount is correct."""
    estimate: FeeEstimate = FeeCalculator.calculate(
        side=OrderSide.BUY,
        price="50000.00",
        is_maker=False,
        quote_size="1000.00",
    )

    assert estimate.is_maker is False
    assert estimate.fee_rate_percent == Decimal("0.09")
    # Trade value 1000.00 * 0.0009 = 0.9000 EUR
    assert estimate.fee_amount == Decimal("0.9000")
    assert estimate.fee_currency == "EUR"
