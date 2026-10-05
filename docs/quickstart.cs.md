# Rychlý start

Tento průvodce vás provede nastavením přístupových údajů, inicializací klienta `RevolutXClient` a první interakcí s burzou.

---

## Nastavení autentizace

Revolut X vyžaduje kryptografické páry klíčů **Ed25519** pro digitální podepisování požadavků.

### 1. Vygenerování páru klíčů Ed25519

Spusťte následující standardní OpenSSL příkazy:

```bash
# Vygenerování soukromého klíče PEM
openssl genpkey -algorithm ed25519 -out keys/private.pem

# Extrakce veřejného klíče PEM
openssl pkey -in keys/private.pem -pubout -out keys/public.pem
```

### 2. Registrace veřejného klíče na Revolut X

1. Přihlaste se do svého účtu na [Revolut X](https://revx.revolut.com).
2. Přejděte do sekce **API Settings** a vytvořte nový API klíč.
3. Vložte obsah vygenerovaného souboru `public.pem`.
4. Zkopírujte vygenerovaný řetězec **API Key**.

### 3. Uložení přihlašovacích údajů do `.env`

Vytvořte soubor `.env` v kořenovém adresáři vaší aplikace:

```ini
REVOLUT_API_KEY=vas_api_klic_zde
REVOLUT_PRIVATE_KEY_PATH=keys/private.pem
```

---

## Inicializace klienta

### Veřejný klient (bez přihlašovacích údajů)
Pokud potřebujete pouze veřejná tržní data (tickery, kniha objednávek, svíčky, pravidla měnových párů), přihlašovací údaje nejsou nutné:

```python
from revolut_x import RevolutXClient

client = RevolutXClient()
print(client.is_authenticated)  # False
```

### Autentizovaný klient
Pro zadávání a rušení objednávek nebo zjišťování zůstatků na účtu předejte API klíč i cestu k privátnímu klíči:

```python
from revolut_x import RevolutXClient

client = RevolutXClient(
    api_key="vas_api_klic_zde",
    private_key_path="keys/private.pem",
)
print(client.is_authenticated)  # True
```
