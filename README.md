# ctxword

Context-aware English vocabulary learning tool for Chinese-speaking programmers.

## Installation

```bash
git clone <repo-url>
cd ctxword
pipx install -e .
```

This installs `t` (and `ctxword`) globally on your `$PATH`.

Alternatively, use a venv and symlink into `~/.local/bin`:

```bash
python -m venv .venv
.venv/bin/pip install -e .
ln -s "$(pwd)/.venv/bin/t" ~/.local/bin/t
```

Or just activate the venv first:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

Set your API key and model in `~/.config/ctxword/config.toml`:

```toml
[llm]
base_url = "https://api.deepseek.com"
api_key_env = "CTXWORD_API_KEY"
model = "deepseek-v4-flash"
```

Then export your key:

```bash
export CTXWORD_API_KEY="sk-your-key-here"
```

Without an API key, `t` falls back to the built-in local dictionary.

## Quick start

```bash
# LLM-powered lookup (default)
t fidelity

# With context
t pending -c "The promise is still pending."

# With context (short flag)
t resolve -c "The promise resolves with the data."

# Look up a phrase
t "race condition"

# Disable LLM, use local dictionary only
t pending --no-ai

# Look up a code identifier
t shouldInvalidateCache --identifier

# View history, review, stats
t history
t review
t stats

# Export to Anki
t export anki -o cards.tsv
```

## Commands

| Command | Description |
|---------|-------------|
| `t WORD` | Look up a word (LLM-powered by default) |
| `t WORD -c TEXT` | Look up with surrounding context |
| `t WORD --no-ai` | Local dictionary only, no API call |
| `t "PHRASE"` | Look up a phrase |
| `t review` | Review due cards |
| `t history` | Show recent lookups |
| `t show QUERY` | Show saved details |
| `t stats` | Show learning statistics |
| `t export anki` | Export cards for Anki |
