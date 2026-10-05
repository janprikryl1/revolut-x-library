# Integrace AI agentů a Skill

Knihovna `revolut-x-library` obsahuje vestavěnou podporu pro **AI vývojové asistenty a autonomní agenty** (jako Google Antigravity, Claude, Cursor, GitHub Copilot nebo vlastní agenty postavené na LangChain či AutoGPT).

---

## Co je to AI Agent Skill?

**Agent Skill** je strukturovaný balíček doménových znalostí, konvencí a operačních postupů, který učí AI agenta spolehlivě psát, testovat a provádět burzovní úlohy s knihovnou `revolut-x-python`.

Skill je definován v repozitáři v cestě:
```text
.agents/skills/revolut-x-library/
├── SKILL.md              # Hlavní instrukce, vzory použití API a pravidla
└── references/
    └── types.md          # Kompletní definice typů a schémata odpovědí
```

### Schopnosti poskytované AI agentům

Když je skill aktivní, AI asistent automaticky rozumí:

- **Autentizaci a nastavení**: Generování Ed25519 klíčů, konfiguraci `RevolutXClient` a ověření `client.is_authenticated`.
- **Exekuci s 0% poplatkem (Maker)**: Výpočtu optimálních maker cen (`calculate_maker_price`) a odesílání `post_only` limitních příkazů pro nulový poplatek.
- **Offline odhadu poplatků**: Použití `FeeCalculator.calculate()` pro kalkulaci poplatků ještě před odesláním objednávky.
- **Validaci pravidel**: Offline validaci parametrů objednávky vůči limitům měnového páru přes `OrderPayloadBuilder.validate_against_pair_rules()` pro předcházení chybám HTTP 400.
- **Přesnosti čísel**: Zachování decimální přesnosti pomocí `Decimal` řetězců namísto floatů.
- **Stránkování a streamování**: Využití `iter_candles()` a `iter_trades()` pro extrakci dat bez narážení na rate-limity.
- **Zpracování výjimek**: Správnému odchytávání konkrétních chyb (`AuthenticationError`, `RateLimitError`, `OrderValidationError`, `ApiError`).

---

## Odkazy a stažení zdrojů pro AI

| Zdroj | Popis | Přímý odkaz |
| :--- | :--- | :--- |
| **`SKILL.md` (Raw)** | Hlavní prompt a instrukce pro AI agenta | [Stáhnout SKILL.md](https://raw.githubusercontent.com/janprikryl1/revolut-x-python/main/.agents/skills/revolut-x-library/SKILL.md) |
| **`types.md` (Raw)** | Přehled typů, enumů a referencí odpovědí | [Stáhnout types.md](https://raw.githubusercontent.com/janprikryl1/revolut-x-python/main/.agents/skills/revolut-x-library/references/types.md) |
| **Složka Skillu (GitHub)** | Interaktivní prohlížeč na GitHubu | [Zobrazit .agents/skills/revolut-x-library](https://github.com/janprikryl1/revolut-x-python/tree/main/.agents/skills/revolut-x-library/) |
| **Repozitář (ZIP)** | Kompletní repozitář včetně skillu a testů | [Stáhnout main.zip](https://github.com/janprikryl1/revolut-x-python/archive/refs/heads/main.zip) |
| **Sesterský PHP Skill** | AI Skill pro sesterské PHP SDK | [Zobrazit revolut-x-php Skill](https://github.com/janprikryl1/revolut-x-php/tree/main/.agents/skills/revolut-x-php/) |

---

## Instalace pro AI prostředí

Agenti mohou knihovnu nainstalovat do svého prostředí následujícími způsoby:

### Standardní PyPI
```bash
pip install revolut-x-python
```

### TestPyPI (Pre-release)
```bash
pip install -i https://test.pypi.org/simple/ revolut-x-python
```

### Přímo z GitHubu
```bash
pip install "git+https://github.com/janprikryl1/revolut-x-python.git#subdirectory=python"
```

---

## Jak skill použít s AI agenty

### 1. Google Antigravity
Skill je umístěn v kořeni repozitáře v `.agents/skills/revolut-x-library/SKILL.md`. Antigravity jej automaticky detekuje a indexuje. Stačí zadat prompt:
> *"Načti aktuální knihu objednávek BTC-EUR a spočítej optimální maker nákupní cenu pro 50 EUR."*

Agent aktivuje skill a použije doporučené vzory přímo v kódu.

### 2. Ostatní asistenti (Claude, Cursor, Copilot)
Můžete soubor `SKILL.md` vložit do kontextu, do `.cursorrules` nebo do systémových promptů.
