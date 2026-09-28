"""Example 3: Account Balances and History (Requires API credentials)."""

import os
from pathlib import Path
from dotenv import load_dotenv
from revolut_x import RevolutXClient

# Load .env
for candidate in (Path(".env"), Path("../.env"), Path("../../.env")):
    if candidate.exists():
        load_dotenv(candidate)
        break


def main():
    api_key = os.getenv("REVOLUT_API_KEY")
    key_path = os.getenv("REVOLUT_PRIVATE_KEY_PATH", "keys/private.pem")

    client = RevolutXClient(api_key=api_key, private_key_path=key_path)

    # 1. Balances
    balances = client.get_balances()
    for b in balances:
        if float(b.get("total", 0)) > 0:
            print(f"Balance: {b['currency']} = {b['available']} (total: {b['total']})")

    # 2. Recent transactions (deposits, settlements, fees)
    txns, _ = client.get_transactions(limit=5)
    print(f"Retrieved {len(txns)} recent transactions.")


if __name__ == "__main__":
    main()
