# ctxword

Context-aware English vocabulary learning tool for Chinese-speaking programmers.

## Installation

```bash
git clone <repo-url>
cd ctxword
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Quick start

```bash
# Look up a word (uses local dictionary, no API key needed)
t pending

# Look up with context
t pending -c "The promise is still pending."

# Look up a phrase
t "race condition"

# Look up a code identifier
t shouldInvalidateCache --identifier

# View history
t history

# Review vocabulary
t review

# View stats
t stats

# Export to Anki
t export anki -o cards.tsv
```

## Configuration

Copy the default config or edit `~/.config/ctxword/config.toml`:

```toml
[llm]
enabled = true
base_url = "https://api.openai.com/v1"
api_key_env = "CTXWORD_API_KEY"
model = "gpt-3.5-turbo"
```

## Commands

| Command | Description |
|---------|-------------|
| `t WORD` | Look up a word |
| `t "PHRASE"` | Look up a phrase |
| `t review` | Review due cards |
| `t history` | Show recent lookups |
| `t show QUERY` | Show saved details |
| `t stats` | Show learning statistics |
| `t export anki` | Export cards for Anki |
