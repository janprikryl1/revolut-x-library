"""Account and wallet methods for the Revolut X API.

This module provides :class:`AccountMixin`, which is mixed into
:class:`~revolut_x.client.RevolutXClient` to add authenticated endpoints
for account balances, transaction history, and private trade history.

All methods in this mixin **require** an API key and private key.
"""

from __future__ import annotations
import logging
from typing import Any, TYPE_CHECKING
from revolut_x.types import Balance, Trade

if TYPE_CHECKING:
    from revolut_x._http import HttpClient

logger = logging.getLogger(__name__)


class AccountMixin:
    """Authenticated account endpoints — balances, transactions, private trades.

    This mixin is not meant to be used directly.  It is mixed into
    :class:`~revolut_x.client.RevolutXClient`.
    """

    # Provided by RevolutXClient
    _http: HttpClient

    # ------------------------------------------------------------------
    # Balances
    # ------------------------------------------------------------------

    def get_balances(self) -> list[Balance]:
        """Retrieve current balances for all currencies on the account.

        Returns:
            A list of :class:`~revolut_x.types.Balance` dictionaries, each
            containing ``currency``, ``available``, ``reserved``, and
            ``total`` fields.

        Raises:
            AuthenticationError: If the client is not authenticated.
            ApiError: If the API returns a non-2xx response.

        Example::

            >>> balances = client.get_balances()
            >>> for b in balances:
            ...     if float(b["total"]) > 0:
            ...         print(f"{b['currency']}: {b['available']} available")
            EUR: 150.00 available
            BTC: 0.00050463 available
        """
        _status, data = self._http.request(
            "GET", "/balances", authenticated=True
        )
        return data if isinstance(data, list) else []

    def get_balance(self, currency: str) -> Balance:
        """Retrieve the balance for a specific currency.

        Args:
            currency: Currency symbol (e.g. ``'EUR'``, ``'BTC'``, ``'ETH'``).
                Case-insensitive.

        Returns:
            A :class:`~revolut_x.types.Balance` dictionary.  If the currency
            is not found on the account, returns a zero-balance entry.

        Raises:
            AuthenticationError: If the client is not authenticated.

        Example::

            >>> eur = client.get_balance("EUR")
            >>> print(f"Available: {eur['available']} EUR")
            Available: 150.00 EUR
        """
        balances = self.get_balances()
        target = currency.upper()

        for item in balances:
            if isinstance(item, dict) and item.get("currency", "").upper() == target:
                return item

        # Currency not found — return zero balance
        return {
            "currency": target,
            "available": "0.00",
            "reserved": "0.00",
            "total": "0.00",
        }

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------

    def get_transactions(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Retrieve account transaction history (ledger).

        Transactions include deposits, withdrawals, trade settlements, and
        fee charges.  Each entry shows the source and destination amounts
        and currencies.

        Args:
            limit: Number of transactions per page (default: 50).
            cursor: Pagination cursor from a previous response.

        Returns:
            A tuple of ``(transactions, next_cursor)``.  Each transaction is
            a dictionary with keys like ``source``, ``destination``,
            ``created_date``, ``processed_date``.  ``next_cursor`` is ``None``
            if there are no more pages.

        Raises:
            AuthenticationError: If the client is not authenticated.

        Example::

            >>> txns, cursor = client.get_transactions(limit=10)
            >>> for tx in txns:
            ...     print(f"{tx['source']['currency']} -> {tx['destination']['currency']}")
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor

        _status, resp = self._http.request(
            "GET", "/transactions", params=params, authenticated=True
        )

        if isinstance(resp, dict):
            transactions = resp.get("data", [])
            next_cursor = resp.get("metadata", {}).get("next_cursor")
        else:
            transactions = resp if isinstance(resp, list) else []
            next_cursor = None

        return transactions, next_cursor

    # ------------------------------------------------------------------
    # Private Trades
    # ------------------------------------------------------------------

    def get_account_trades(
        self,
        symbol: str,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Trade], str | None]:
        """Retrieve private (your own) trade history for a trading pair.

        Unlike public trades from :meth:`get_trades`, these are your
        personal executed trades with full fee information.

        Args:
            symbol: Trading pair (e.g. ``'BTC-EUR'``).
            limit: Number of trades per page (default: 50).
            cursor: Pagination cursor from a previous response.

        Returns:
            A tuple of ``(trades, next_cursor)`` where ``trades`` is a list
            of :class:`~revolut_x.types.Trade` dicts with your private
            execution details.

        Raises:
            AuthenticationError: If the client is not authenticated.
            ApiError: If the API returns a non-2xx response.

        Example::

            >>> trades, cursor = client.get_account_trades("BTC-EUR", limit=10)
            >>> for t in trades:
            ...     print(f"{t['side']} {t['quantity']} BTC @ {t['price']} EUR")
        """
        api_symbol = symbol.replace("/", "-").upper()
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor

        _status, resp = self._http.request(
            "GET",
            f"/trades/private/{api_symbol}",
            params=params,
            authenticated=True,
        )

        if isinstance(resp, dict):
            trades = resp.get("data", [])
            next_cursor = resp.get("metadata", {}).get("next_cursor")
        else:
            trades = resp if isinstance(resp, list) else []
            next_cursor = None

        return trades, next_cursor
