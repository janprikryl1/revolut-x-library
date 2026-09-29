"""Unit tests for OrdersMixin in revolut_x.orders."""

from __future__ import annotations
from typing import Any
from unittest.mock import MagicMock
import pytest

from revolut_x.orders import OrdersMixin
from revolut_x.types import OrderSide, OrderType, TimeInForce


class DummyClient(OrdersMixin):
    def __init__(self) -> None:
        self._http = MagicMock()


def test_place_order_market_unified() -> None:
    client = DummyClient()
    client._http.request.return_value = (
        200,
        {"data": [{"venue_order_id": "test-order-1", "state": "new"}]},
    )

    resp = client.place_order(
        "BTC-EUR",
        OrderSide.BUY,
        order_type=OrderType.MARKET,
        quote_size="50.00",
    )

    assert resp["venue_order_id"] == "test-order-1"
    client._http.request.assert_called_once()
    args, kwargs = client._http.request.call_args
    assert args == ("POST", "/orders")
    assert kwargs["authenticated"] is True
    body = kwargs["json_body"]
    assert body["symbol"] == "BTC-EUR"
    assert body["side"] == "buy"
    assert "market" in body["order_configuration"]
    assert body["order_configuration"]["market"]["quote_size"] == "50.00"


def test_place_order_limit_unified() -> None:
    client = DummyClient()
    client._http.request.return_value = (
        200,
        {"venue_order_id": "test-order-2", "state": "new"},
    )

    resp = client.place_order(
        "BTC/EUR",
        "sell",
        order_type="limit",
        price="85000.00",
        base_size="0.01",
        post_only=True,
    )

    assert resp["venue_order_id"] == "test-order-2"
    args, kwargs = client._http.request.call_args
    body = kwargs["json_body"]
    assert body["symbol"] == "BTC-EUR"
    assert body["side"] == "sell"
    assert "limit" in body["order_configuration"]
    limit_conf = body["order_configuration"]["limit"]
    assert limit_conf["price"] == "85000.00"
    assert limit_conf["base_size"] == "0.01"
    assert "post_only" in limit_conf["execution_instructions"]


def test_place_order_raw_dict_payload() -> None:
    client = DummyClient()
    client._http.request.return_value = (
        200,
        {"data": [{"venue_order_id": "raw-order-id", "state": "new"}]},
    )

    raw_payload = {
        "symbol": "BTC-EUR",
        "side": "buy",
        "order_configuration": {"market": {"quote_size": "100.00"}},
    }

    resp = client.place_order(raw_payload)
    assert resp["venue_order_id"] == "raw-order-id"
    args, kwargs = client._http.request.call_args
    assert kwargs["json_body"] == raw_payload


def test_place_order_missing_side_raises() -> None:
    client = DummyClient()
    with pytest.raises(ValueError) as exc_info:
        client.place_order("BTC-EUR")
    assert "Parameter 'side'" in str(exc_info.value)


def test_place_market_order_wrapper() -> None:
    client = DummyClient()
    client._http.request.return_value = (
        200,
        {"data": [{"venue_order_id": "mkt-wrap", "state": "new"}]},
    )

    resp = client.place_market_order("BTC-EUR", OrderSide.BUY, quote_size="25.00")
    assert resp["venue_order_id"] == "mkt-wrap"
    args, kwargs = client._http.request.call_args
    body = kwargs["json_body"]
    assert "market" in body["order_configuration"]
    assert body["order_configuration"]["market"]["quote_size"] == "25.00"


def test_place_limit_order_wrapper() -> None:
    client = DummyClient()
    client._http.request.return_value = (
        200,
        {"data": [{"venue_order_id": "lmt-wrap", "state": "new"}]},
    )

    resp = client.place_limit_order(
        "BTC-EUR",
        OrderSide.SELL,
        price="90000.00",
        base_size="0.02",
        post_only=True,
    )
    assert resp["venue_order_id"] == "lmt-wrap"
    args, kwargs = client._http.request.call_args
    body = kwargs["json_body"]
    assert "limit" in body["order_configuration"]
    assert body["order_configuration"]["limit"]["price"] == "90000.00"
    assert "post_only" in body["order_configuration"]["limit"]["execution_instructions"]
