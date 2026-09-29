"""Order management methods for the Revolut X API.

This module provides :class:`OrdersMixin`, which is mixed into
:class:`~revolut_x.client.RevolutXClient` to add authenticated endpoints
for placing, inspecting, and canceling orders.

All methods in this mixin **require** an API key and private key.
"""

from __future__ import annotations
import logging
from decimal import Decimal
from typing import Any, TYPE_CHECKING
from revolut_x.types import (
    Fill,
    OrderDetail,
    OrderResponse,
    OrderSide,
    OrderType,
    TimeInForce,
)
from revolut_x.helpers import OrderPayloadBuilder, calculate_maker_price

if TYPE_CHECKING:
    from revolut_x._http import HttpClient

logger = logging.getLogger(__name__)


class OrdersMixin:
    """Authenticated order management endpoints.

    This mixin is not meant to be used directly.  It is mixed into
    :class:`~revolut_x.client.RevolutXClient`.
    """

    # Provided by RevolutXClient
    _http: HttpClient

    # ------------------------------------------------------------------
    # Place orders
    # ------------------------------------------------------------------

    def place_order(
        self,
        symbol_or_payload: str | dict[str, Any],
        side: OrderSide | str | None = None,
        *,
        order_type: OrderType | str = OrderType.MARKET,
        price: str | None = None,
        base_size: str | None = None,
        quote_size: str | None = None,
        post_only: bool = False,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
        client_order_id: str | None = None,
    ) -> OrderResponse:
        """Submit an order to the exchange.

        This method supports two calling styles:

        1. **Unified high-level placement** (recommended)::

            >>> # Market order
            >>> order = client.place_order("BTC-EUR", OrderSide.BUY, order_type="market", quote_size="50.00")
            >>> # Limit order
            >>> order = client.place_order("BTC-EUR", OrderSide.BUY, order_type="limit", price="80000.00", quote_size="50.00")

        2. **Low-level raw payload dictionary** (backward compatible)::

            >>> payload = OrderPayloadBuilder.build_market_order("BTC-EUR", OrderSide.BUY, quote_size="50.00")
            >>> order = client.place_order(payload)

        Args:
            symbol_or_payload: Trading pair (e.g. ``'BTC-EUR'``) or a complete payload dict.
            side: :attr:`OrderSide.BUY` or :attr:`OrderSide.SELL` (required if symbol string is given).
            order_type: :attr:`OrderType.MARKET` (default) or :attr:`OrderType.LIMIT`.
            price: Limit price in quote currency (required for limit orders, omitted for market orders).
            base_size: Amount in the base currency (e.g. ``'0.001'`` BTC). Mutually exclusive with ``quote_size``.
            quote_size: Amount in the quote currency (e.g. ``'50.00'`` EUR). Mutually exclusive with ``base_size``.
            post_only: If ``True``, guarantees the order enters the book as a maker (0% fee, limit orders only).
            time_in_force: :attr:`TimeInForce.GTC` (default) or :attr:`TimeInForce.IOC` (limit orders only).
            client_order_id: Optional client UUID for idempotency. Auto-generated if not provided.

        Returns:
            An :class:`~revolut_x.types.OrderResponse` with the assigned
            ``venue_order_id`` and initial ``state``.

        Raises:
            ValueError / OrderValidationError: If order parameters are invalid or missing.
            AuthenticationError: If the client is not authenticated.
            ApiError: If the exchange rejects the order.

        Example::

            >>> order = client.place_order(
            ...     "BTC-EUR", OrderSide.BUY, order_type="market", quote_size="50.00"
            ... )
            >>> print(f"Order ID: {order['venue_order_id']}")
        """
        if isinstance(symbol_or_payload, dict):
            payload = symbol_or_payload
        else:
            if side is None:
                raise ValueError("Parameter 'side' (OrderSide.BUY / OrderSide.SELL) is required when placing an order by symbol.")
            payload = OrderPayloadBuilder.build_order(
                symbol=symbol_or_payload,
                side=side,
                order_type=order_type,
                price=price,
                base_size=base_size,
                quote_size=quote_size,
                post_only=post_only,
                time_in_force=time_in_force,
                client_order_id=client_order_id,
            )

        _status, resp = self._http.request(
            "POST", "/orders", json_body=payload, authenticated=True
        )

        # API wraps response in {"data": [...]} or {"data": {...}}
        data = resp.get("data", resp) if isinstance(resp, dict) else resp
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data

    def place_market_order(
        self,
        symbol: str,
        side: OrderSide | str,
        *,
        base_size: str | None = None,
        quote_size: str | None = None,
        client_order_id: str | None = None,
    ) -> OrderResponse:
        """Place a market order (immediate execution, 0.09% taker fee).

        Convenience wrapper around :meth:`place_order` with ``order_type=OrderType.MARKET``.

        Exactly **one** of ``base_size`` or ``quote_size`` must be provided.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            side: :attr:`OrderSide.BUY` or :attr:`OrderSide.SELL`.
            base_size: Amount in the base currency (e.g. ``'0.001'`` BTC).
                Mutually exclusive with ``quote_size``.
            quote_size: Amount in the quote currency (e.g. ``'50.00'`` EUR).
                Mutually exclusive with ``base_size``.
            client_order_id: Optional UUID for idempotency.  Auto-generated
                if not provided.

        Returns:
            An :class:`~revolut_x.types.OrderResponse` with the exchange
            order ID.

        Raises:
            ValueError: If neither or both of ``base_size``/``quote_size``
                are provided.
            AuthenticationError: If the client is not authenticated.
            ApiError: If the exchange rejects the order.

        Example::

            >>> order = client.place_market_order(
            ...     "BTC-EUR", OrderSide.BUY, quote_size="50.00"
            ... )
            >>> print(f"Bought BTC, order ID: {order['venue_order_id']}")
        """
        return self.place_order(
            symbol_or_payload=symbol,
            side=side,
            order_type=OrderType.MARKET,
            base_size=base_size,
            quote_size=quote_size,
            client_order_id=client_order_id,
        )

    def place_limit_order(
        self,
        symbol: str,
        side: OrderSide | str,
        price: str,
        *,
        base_size: str | None = None,
        quote_size: str | None = None,
        post_only: bool = False,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
        client_order_id: str | None = None,
    ) -> OrderResponse:
        """Place a limit order at a specific price.

        Convenience wrapper around :meth:`place_order` with ``order_type=OrderType.LIMIT``.

        Exactly **one** of ``base_size`` or ``quote_size`` must be provided.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            side: :attr:`OrderSide.BUY` or :attr:`OrderSide.SELL`.
            price: Limit price in the quote currency (e.g. ``'85000.00'`` EUR
                per 1 BTC).
            base_size: Amount in the base currency.  Mutually exclusive
                with ``quote_size``.
            quote_size: Amount in the quote currency.  Mutually exclusive
                with ``base_size``.
            post_only: If ``True``, guarantees the order enters the book
                as a **maker** (0% fee).  If it would match immediately
                (taker), the exchange rejects it.
            time_in_force: :attr:`TimeInForce.GTC` (good 'til canceled,
                default) or :attr:`TimeInForce.IOC` (immediate or cancel).
            client_order_id: Optional UUID for idempotency.

        Returns:
            An :class:`~revolut_x.types.OrderResponse`.

        Raises:
            ValueError: If neither or both of ``base_size``/``quote_size``
                are provided.
            AuthenticationError: If the client is not authenticated.
            ApiError: If the exchange rejects the order.

        Example::

            >>> order = client.place_limit_order(
            ...     "BTC-EUR", OrderSide.BUY, price="80000.00",
            ...     quote_size="50.00", post_only=True,
            ... )
            >>> print(f"Limit order placed: {order['venue_order_id']}")
        """
        return self.place_order(
            symbol_or_payload=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            price=price,
            base_size=base_size,
            quote_size=quote_size,
            post_only=post_only,
            time_in_force=time_in_force,
            client_order_id=client_order_id,
        )

    def calculate_maker_price(
        self,
        symbol: str,
        side: OrderSide | str,
        *,
        offset: Any = Decimal("0.10"),
        tick_size: Any = Decimal("0.01"),
    ) -> Decimal:
        """Fetch current ticker for symbol and calculate the optimal Maker price.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            side: :attr:`OrderSide.BUY` or :attr:`OrderSide.SELL`.
            offset: Offset in quote currency (default: ``0.10``).
            tick_size: Price tick size for quantisation (default: ``0.01``).

        Returns:
            Decimal: The optimal limit price for a zero-fee Maker order.
        """
        get_ticker_fn = getattr(self, "get_ticker", None)
        if get_ticker_fn is None:
            raise RuntimeError("get_ticker is not available on this client instance.")
        ticker = get_ticker_fn(symbol)
        return calculate_maker_price(
            side=side,
            best_bid=ticker.get("bid"),
            best_ask=ticker.get("ask"),
            last_price=ticker.get("last_price"),
            offset=offset,
            tick_size=tick_size,
        )

    def place_maker_order(
        self,
        symbol: str,
        side: OrderSide | str,
        *,
        price: str | None = None,
        offset: Any = Decimal("0.10"),
        tick_size: Any = Decimal("0.01"),
        base_size: str | None = None,
        quote_size: str | None = None,
        time_in_force: TimeInForce | str = TimeInForce.GTC,
        client_order_id: str | None = None,
    ) -> OrderResponse:
        """Place a guaranteed zero-fee Maker limit order (0.00% fee).

        If ``price`` is not explicitly provided, this method automatically fetches
        the latest market ticker and computes an optimal Maker price with the given
        ``offset``:
        - For BUY: ``best_bid - offset``
        - For SELL: ``best_ask + offset``

        The order is submitted with ``post_only=True``, ensuring the exchange will
        accept it as a Maker (0% fee) or reject it if it would match immediately.

        Exactly **one** of ``base_size`` or ``quote_size`` must be provided.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            side: :attr:`OrderSide.BUY` or :attr:`OrderSide.SELL`.
            price: Optional fixed limit price. If omitted, calculated dynamically.
            offset: Offset in quote currency from best bid/ask (default: ``0.10``).
            tick_size: Minimum price increment for quantisation (default: ``0.01``).
            base_size: Amount in the base currency (e.g. ``'0.001'`` BTC).
            quote_size: Amount in the quote currency (e.g. ``'50.00'`` EUR).
            time_in_force: :attr:`TimeInForce.GTC` (default) or :attr:`TimeInForce.IOC`.
            client_order_id: Optional UUID for idempotency.

        Returns:
            An :class:`~revolut_x.types.OrderResponse` from the exchange.

        Raises:
            ValueError / OrderValidationError: If sizes or side are invalid.
            AuthenticationError: If the client is not authenticated.
            ApiError: If the exchange rejects the order.

        Example::

            >>> # Buy BTC for 50 EUR with zero fee at optimal Maker price:
            >>> order = client.place_maker_order("BTC-EUR", OrderSide.BUY, quote_size="50.00")
            >>> print(f"Maker order placed: {order['venue_order_id']}")
        """
        if price is None:
            calc_price = str(self.calculate_maker_price(symbol, side, offset=offset, tick_size=tick_size))
        else:
            calc_price = str(price)

        return self.place_limit_order(
            symbol=symbol,
            side=side,
            price=calc_price,
            base_size=base_size,
            quote_size=quote_size,
            post_only=True,
            time_in_force=time_in_force,
            client_order_id=client_order_id,
        )

    # ------------------------------------------------------------------
    # Query orders
    # ------------------------------------------------------------------

    def get_order(self, order_id: str) -> OrderDetail:
        """Retrieve detailed information about a specific order.

        Args:
            order_id: The exchange-assigned order ID (``venue_order_id``).

        Returns:
            An :class:`~revolut_x.types.OrderDetail` with status, filled
            quantity, average fill price, total fee, and timestamps.

        Raises:
            AuthenticationError: If the client is not authenticated.
            ApiError: If the order is not found (HTTP 404) or other error.

        Example::

            >>> detail = client.get_order("7a52e92e-8639-4fe1-abaa-68d3a2d5234b")
            >>> print(f"Status: {detail['status']}, Fee: {detail['total_fee']} EUR")
        """
        _status, resp = self._http.request(
            "GET", f"/orders/{order_id}", authenticated=True
        )
        if isinstance(resp, dict) and "data" in resp:
            return resp["data"]
        return resp

    def get_order_fills(self, order_id: str) -> list[Fill]:
        """Retrieve individual fills (partial executions) for an order.

        Each fill includes the execution price, quantity, and whether it
        was a maker or taker trade (``im`` field).

        Args:
            order_id: The exchange-assigned order ID (``venue_order_id``).

        Returns:
            A list of :class:`~revolut_x.types.Fill` dictionaries.
            The ``im`` field is ``True`` for maker fills (0% fee) and
            ``False`` for taker fills (0.09% fee).

        Raises:
            AuthenticationError: If the client is not authenticated.
            ApiError: If the order is not found or other error.

        Example::

            >>> fills = client.get_order_fills("7a52e92e-...")
            >>> for fill in fills:
            ...     fee_type = "maker (0%)" if fill["im"] else "taker (0.09%)"
            ...     print(f"{fill['q']} BTC @ {fill['p']} EUR [{fee_type}]")
        """
        _status, resp = self._http.request(
            "GET", f"/orders/fills/{order_id}", authenticated=True
        )
        if isinstance(resp, dict) and "data" in resp:
            return resp["data"]
        return resp

    def get_active_orders(
        self, symbol: str | None = None
    ) -> list[OrderDetail]:
        """Retrieve all currently open (active) orders.

        Args:
            symbol: Optional filter by trading pair (e.g. ``'BTC-EUR'``).
                If ``None``, returns active orders for all pairs.

        Returns:
            A list of :class:`~revolut_x.types.OrderDetail` dictionaries.

        Raises:
            AuthenticationError: If the client is not authenticated.
        """
        params: dict[str, Any] | None = None
        if symbol:
            params = {"symbol": symbol.replace("/", "-").upper()}

        _status, resp = self._http.request(
            "GET", "/orders/active", params=params, authenticated=True
        )
        if isinstance(resp, dict) and "data" in resp:
            return resp["data"]
        return resp if isinstance(resp, list) else []

    def get_historical_orders(
        self,
        symbol: str | None = None,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[OrderDetail], str | None]:
        """Retrieve historical (completed/canceled) orders with pagination.

        Args:
            symbol: Optional filter by trading pair.
            limit: Number of orders per page (default: 50).
            cursor: Pagination cursor from a previous response.

        Returns:
            A tuple of ``(orders, next_cursor)``.  ``next_cursor`` is ``None``
            if there are no more pages.

        Raises:
            AuthenticationError: If the client is not authenticated.
        """
        params: dict[str, Any] = {"limit": limit}
        if symbol:
            params["symbol"] = symbol.replace("/", "-").upper()
        if cursor:
            params["cursor"] = cursor

        _status, resp = self._http.request(
            "GET", "/orders/historical", params=params, authenticated=True
        )

        if isinstance(resp, dict):
            orders = resp.get("data", [])
            next_cursor = resp.get("metadata", {}).get("next_cursor")
        else:
            orders = resp if isinstance(resp, list) else []
            next_cursor = None

        return orders, next_cursor

    # ------------------------------------------------------------------
    # Cancel orders
    # ------------------------------------------------------------------

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        """Cancel a specific open order.

        Args:
            order_id: The exchange-assigned order ID (``venue_order_id``).

        Returns:
            The API response confirming cancellation.

        Raises:
            AuthenticationError: If the client is not authenticated.
            ApiError: If the order cannot be canceled (e.g. already filled,
                not found).

        Example::

            >>> client.cancel_order("7a52e92e-8639-4fe1-abaa-68d3a2d5234b")
        """
        _status, resp = self._http.request(
            "DELETE", f"/orders/{order_id}", authenticated=True
        )
        return resp

    def cancel_all_orders(
        self, symbol: str | None = None
    ) -> dict[str, Any]:
        """Cancel all open orders, optionally filtered by trading pair.

        Args:
            symbol: If provided, only cancel orders for this pair
                (e.g. ``'BTC-EUR'``).  If ``None``, cancel **all** open
                orders across all pairs.

        Returns:
            The API response confirming cancellation.

        Raises:
            AuthenticationError: If the client is not authenticated.

        Example::

            >>> client.cancel_all_orders("BTC-EUR")
        """
        params: dict[str, Any] | None = None
        if symbol:
            params = {"symbol": symbol.replace("/", "-").upper()}

        _status, resp = self._http.request(
            "DELETE", "/orders", params=params, authenticated=True
        )
        return resp
