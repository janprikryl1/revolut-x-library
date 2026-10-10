# Smart Maker Order Strategy (0.00% fee)

One of the biggest advantages of trading on the **Revolut X** exchange is its fee structure:

| Execution type | Fee | Description |
| :--- | :--- | :--- |
| **Maker** | **0.00 %** | The order adds liquidity to the order book (limit order). |
| **Taker** | **0.09 %** | The order removes liquidity (market order, or a limit order matched aggressively). |

At larger volumes or in algorithmic trading, the difference between 0.00 % and 0.09 % amounts to a substantial cost saving.

---

## How `post_only` Protection Works

When you submit a limit order, the market price may move and the order may match against the other side immediately. In that case the exchange would charge the **0.09% (Taker)** fee.

The `post_only = true` flag:
- Guarantees that the order enters the order book exclusively as a **Maker**.
- If the order would execute immediately as a Taker, the exchange rejects/cancels it right away at no fee.

---

## Dynamic Maker Price Calculation

The library includes a dedicated `MakerOrderStrategy` class that computes the optimal limit price from the live market state, with a safety offset:

- **For BUY**:
  $$\text{price} = \text{best\_bid} - \text{offset}$$
- **For SELL**:
  $$\text{price} = \text{best\_ask} + \text{offset}$$

The price is then rounded to a valid price increment for the trading pair (`tick_size`).

---

## Usage Examples

=== "Python"

    ```python
    from revolut_x import RevolutXClient, OrderSide

    client = RevolutXClient(api_key="...", private_key_path="keys/private.pem")

    # Fetches the current bid/ask, applies a 0.10 EUR offset and submits with post_only=True
    order = client.place_maker_order(
        symbol="BTC-EUR",
        side=OrderSide.BUY,
        quote_size="50.00",
        offset="0.10",
    )
    ```

=== "PHP"

    ```php
    use RevolutX\Client;
    use RevolutX\Types\OrderSide;

    $client = new Client(apiKey: '...', privateKeyPath: 'keys/private.pem');

    // Fetches the current bid/ask, applies a 0.10 EUR offset and submits with post_only=True
    $order = $client->placeMakerOrder(
        symbol: 'BTC-EUR',
        side: OrderSide::BUY,
        quoteSize: '50.00',
        offset: '0.10'
    );
    ```
