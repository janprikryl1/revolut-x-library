"""Unit tests for Maker pricing strategy and zero-fee order placement."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock
import pytest

from revolut_x.exceptions import OrderValidationError
from revolut_x.helpers import (
    OrderPayloadBuilder,
    build_maker_order,
    calculate_maker_price,
)
from revolut_x.orders import OrdersMixin
from revolut_x.types import OrderSide, TimeInForce


class DummyFullClient(OrdersMixin):
    """Mock client combining MarketMixin-like get_ticker and OrdersMixin."""

    def __init__(self) -> None:
        self._http = MagicMock()
        self.get_ticker = MagicMock()


def test_calculate_maker_price_buy() -> None:
    """Test BUY price calculation: best_bid - offset."""
    price = calculate_maker_price(
        side=OrderSide.BUY,
        best_bid="80000.00",
        best_ask="80000.50",
        offset="0.10",
    )
    assert price == Decimal("79999.90")

    # With string side
    price_str = calculate_maker_price(
        side="buy",
        best_bid=80000.00,
        offset=0.25,
    )
    assert price_str == Decimal("79999.75")


def test_calculate_maker_price_sell() -> None:
    """Test SELL price calculation: best_ask + offset."""
    price = calculate_maker_price(
        side=OrderSide.SELL,
        best_bid="80000.00",
        best_ask="80000.50",
        offset="0.10",
    )
    assert price == Decimal("80000.60")

    # With string side
    price_str = calculate_maker_price(
        side="sell",
        best_ask="80000.50",
        offset="0.05",
    )
    assert price_str == Decimal("80000.55")


def test_calculate_maker_price_fallback_last_price() -> None:
    """Test fallback to last_price when bid/ask is not available."""
    price_buy = calculate_maker_price(
        side=OrderSide.BUY,
        best_bid=None,
        last_price="75000.00",
        offset="1.00",
    )
    assert price_buy == Decimal("74999.00")

    price_sell = calculate_maker_price(
        side=OrderSide.SELL,
        best_ask=None,
        last_price="75000.00",
        offset="1.00",
    )
    assert price_sell == Decimal("75001.00")


def test_calculate_maker_price_missing_references_raises() -> None:
    """Test that OrderValidationError is raised when no reference price is given."""
    with pytest.raises(OrderValidationError) as exc_buy:
        calculate_maker_price(side=OrderSide.BUY)
    assert "neither 'best_bid' nor 'last_price'" in str(exc_buy.value)

    with pytest.raises(OrderValidationError) as exc_sell:
        calculate_maker_price(side=OrderSide.SELL)
    assert "neither 'best_ask' nor 'last_price'" in str(exc_sell.value)


def test_calculate_maker_price_invalid_side() -> None:
    """Test that invalid side raises OrderValidationError."""
    with pytest.raises(OrderValidationError):
        calculate_maker_price(side="hold", best_bid="80000.00")


def test_build_maker_order_payload() -> None:
    """Test build_maker_order creates limit order with post_only=True."""
    payload = build_maker_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        price="79999.90",
        quote_size="50.00",
    )

    assert payload["symbol"] == "BTC-EUR"
    assert payload["side"] == "buy"
    limit_conf = payload["order_configuration"]["limit"]
    assert limit_conf["price"] == "79999.90"
    assert limit_conf["quote_size"] == "50.00"
    assert "post_only" in limit_conf["execution_instructions"]
    assert "allow_taker" not in limit_conf["execution_instructions"]


def test_client_calculate_maker_price() -> None:
    """Test client.calculate_maker_price fetches ticker and calculates price."""
    client = DummyFullClient()
    client.get_ticker.return_value = {
        "symbol": "BTC-EUR",
        "bid": "74200.00",
        "ask": "74201.00",
        "last_price": "74200.50",
    }

    price_buy = client.calculate_maker_price("BTC-EUR", OrderSide.BUY, offset="0.10")
    assert price_buy == Decimal("74199.90")
    client.get_ticker.assert_called_with("BTC-EUR")

    price_sell = client.calculate_maker_price("BTC-EUR", OrderSide.SELL, offset="0.10")
    assert price_sell == Decimal("74201.10")


def test_client_place_maker_order_dynamic() -> None:
    """Test client.place_maker_order fetches ticker and submits post_only order."""
    client = DummyFullClient()
    client.get_ticker.return_value = {
        "symbol": "BTC-EUR",
        "bid": "70000.00",
        "ask": "70001.00",
    }
    client._http.request.return_value = (
        200,
        {"data": [{"venue_order_id": "maker-order-1", "state": "new"}]},
    )

    resp = client.place_maker_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        quote_size="100.00",
        offset="0.20",
    )

    assert resp["venue_order_id"] == "maker-order-1"
    args, kwargs = client._http.request.call_args
    body = kwargs["json_body"]
    limit_conf = body["order_configuration"]["limit"]
    assert limit_conf["price"] == "69999.80"
    assert limit_conf["quote_size"] == "100.00"
    assert "post_only" in limit_conf["execution_instructions"]


def test_client_place_maker_order_explicit_price() -> None:
    """Test client.place_maker_order with explicitly provided price bypasses ticker."""
    client = DummyFullClient()
    client._http.request.return_value = (
        200,
        {"data": [{"venue_order_id": "maker-order-2", "state": "new"}]},
    )

    resp = client.place_maker_order(
        symbol="BTC-EUR",
        side=OrderSide.SELL,
        price="75000.00",
        base_size="0.05",
    )

    assert resp["venue_order_id"] == "maker-order-2"
    client.get_ticker.assert_not_called()
    args, kwargs = client._http.request.call_args
    body = kwargs["json_body"]
    limit_conf = body["order_configuration"]["limit"]
    assert limit_conf["price"] == "75000.00"
    assert limit_conf["base_size"] == "0.05"
    assert "post_only" in limit_conf["execution_instructions"]
