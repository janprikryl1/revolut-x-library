# AI Agent Integration & Skill

The `revolut-x-library` includes built-in support for **AI coding assistants and autonomous agents** (such as Google Antigravity, Claude, Cursor, GitHub Copilot, and custom LangChain/AutoGPT agents).

---

## What is the AI Agent Skill?

An **Agent Skill** is a structured package of domain knowledge, conventions, and operational workflows that teaches an AI agent how to reliably write, test, and execute trading workflows with `revolut-x-python`.

The skill is defined in:
```text
.agents/skills/revolut-x-library/
├── SKILL.md              # Core instructions, API patterns, and rules
└── references/
    └── types.md          # Complete type definitions and payload schemas
```

### Capabilities Provided to AI Agents

When the skill is active, the AI assistant automatically understands:

- **Authentication & Setup**: Generating Ed25519 keys, configuring `RevolutXClient`, and verifying `client.is_authenticated`.
- **Zero-Fee Maker Execution**: Calculating optimal maker prices (`calculate_maker_price`) and submitting `post_only` limit orders to ensure 0.00% maker fee.
- **Offline Fee Estimation**: Using `FeeCalculator.calculate()` to project fees before placing orders.
- **Rule Validation**: Validating payloads offline against pair rules via `OrderPayloadBuilder.validate_against_pair_rules()` to avoid 400 errors.
- **Decimal Precision**: Preserving decimal precision with `Decimal` strings instead of floats.
- **Pagination & Streaming**: Using `iter_candles()` and `iter_trades()` for data extraction without hitting rate limits.
- **Exception Handling**: Catching specific errors (`AuthenticationError`, `RateLimitError`, `OrderValidationError`, `ApiError`).

---

## Downloads & AI Resources

| Asset | Description | Direct Link |
| :--- | :--- | :--- |
| **`SKILL.md` (Raw)** | Core AI agent prompt and instructions | [Download SKILL.md](https://raw.githubusercontent.com/janprikryl1/revolut-x-python/main/.agents/skills/revolut-x-library/SKILL.md) |
| **`types.md` (Raw)** | Types, enums, and response schemas | [Download types.md](https://raw.githubusercontent.com/janprikryl1/revolut-x-python/main/.agents/skills/revolut-x-library/references/types.md) |
| **Skill Folder (GitHub)** | Interactive folder browser on GitHub | [View .agents/skills/revolut-x-library](https://github.com/janprikryl1/revolut-x-python/tree/main/.agents/skills/revolut-x-library/) |
| **Repository (ZIP)** | Complete repository including skill & tests | [Download main.zip](https://github.com/janprikryl1/revolut-x-python/archive/refs/heads/main.zip) |
| **PHP Sister Skill** | AI Skill for the PHP SDK | [View revolut-x-php Skill](https://github.com/janprikryl1/revolut-x-php/tree/main/.agents/skills/revolut-x-php/) |

---

## Installation for AI Workflows

Agents can install the library into their execution environment using any of the following methods:

### Standard PyPI
```bash
pip install revolut-x-python
```

### TestPyPI (Pre-release)
```bash
pip install -i https://test.pypi.org/simple/ revolut-x-python
```

### Direct from GitHub
```bash
pip install "git+https://github.com/janprikryl1/revolut-x-library.git#subdirectory=python"
```

### From Local Clone / Downloaded ZIP
```bash
git clone https://github.com/janprikryl1/revolut-x-library.git
cd revolut-x-library/python
pip install -e .
```

---

## How to Use with AI Agents

### 1. Google Antigravity
The skill is located at `.agents/skills/revolut-x-library/SKILL.md` in the workspace root. Antigravity automatically discovers it. You can simply ask:
> *"Fetch the current BTC-EUR order book and calculate an optimal maker buy price for 50 EUR."*

The agent activates the skill and uses the recommended patterns directly.

### 2. Other AI Assistants (Claude, Cursor, Copilot)
You can include or reference `.agents/skills/revolut-x-library/SKILL.md` as context or in custom agent instructions (e.g. `.cursorrules` or system prompt) to equip the model with full library knowledge.
