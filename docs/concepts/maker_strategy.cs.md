# Smart Maker Order Strategie (0.00% poplatek)

Jednou z největších výhod obchodování na burze **Revolut X** je cenová struktura poplatků:

| Typ exekuce | Poplatek | Popis |
| :--- | :--- | :--- |
| **Maker** | **0.00 %** | Příkaz přidává likviditu do knihy objednávek (Limit order). |
| **Taker** | **0.09 %** | Příkaz odebírá likviditu (Market order nebo Limit agresivně spárovaný). |

Při větších objemech nebo algoritmickém obchodování představuje rozdíl mezi 0.00 % a 0.09 % zásadní úsporu nákladů.

---

## Jak funguje ochrana `post_only`

Při odeslání limitního příkazu hrozí, že se cena na trhu posune a příkaz se okamžitě spáruje s protistranou. V takovém případě by burza naúčtovala poplatek **0.09% (Taker)**.

Příznak `post_only = true`:
- Zaručuje, že příkaz vstoupí do knihy objednávek výhradně jako **Maker**.
- Pokud by se příkaz měl okamžitě realizovat jako Taker, burza jej okamžitě odmítne/zruší bez jakéhokoliv poplatku.

---

## Dynamický výpočet Maker ceny

Knihovna obsahuje specializovanou třídu `MakerOrderStrategy`, která na základě živého stavu trhu vypočítá optimální limitní cenu s bezpečnostním offsetem:

- **Pro NÁKUP (BUY)**:
  $$\text{cena} = \text{best\_bid} - \text{offset}$$
- **Pro PRODEJ (SELL)**:
  $$\text{cena} = \text{best\_ask} + \text{offset}$$

Příkaz je následně zaokrouhlen na platnou velikost cenového kroku měnového páru (`tick_size`).

---

## Příklady použití

=== "Python"

    ```python
    from revolut_x import RevolutXClient, OrderSide

    client = RevolutXClient(api_key="...", private_key_path="keys/private.pem")

    # Automaticky stáhne aktuální bid/ask, aplikuje offset 0.10 EUR a odešle s post_only=True
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

    // Automaticky stáhne aktuální bid/ask, aplikuje offset 0.10 EUR a odešle s post_only=True
    $order = $client->placeMakerOrder(
        symbol: 'BTC-EUR',
        side: OrderSide::BUY,
        quoteSize: '50.00',
        offset: '0.10'
    );
    ```
