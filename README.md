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

All settings are read from environment variables. No config file needed.

```bash
export CTXWORD_OPENAI_KEY="sk-your-key-here"
export CTXWORD_OPENAI_BASE="https://api.deepseek.com"  # default: OpenAI
export CTXWORD_MODEL="deepseek-v4-flash"                # default: gpt-3.5-turbo
```

| Variable | Default | Description |
|----------|---------|-------------|
| `CTXWORD_OPENAI_KEY` | (none) | API key |
| `CTXWORD_OPENAI_BASE` | `https://api.openai.com/v1` | API base URL |
| `CTXWORD_MODEL` | `gpt-3.5-turbo` | Model name |
| `CTXWORD_MAX_TOKENS` | `2048` | Max response tokens |
| `CTXWORD_TEMPERATURE` | `0.2` | LLM temperature |
| `CTXWORD_LLM_ENABLED` | `1` | Set to `0` to disable LLM |

Without `CTXWORD_OPENAI_KEY`, `t` falls back to the built-in local dictionary.

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

## Shell tab completion

`t` can autocomplete words as you type using a built-in ~2500-word English dictionary.

```bash
# One-time setup
t completion

# Then add to your shell config:
# bash (~/.bashrc):
source ~/.local/share/ctxword/completion.bash

# zsh (~/.zshrc):
source ~/.local/share/ctxword/completion.zsh
```

Restart your shell, then type `t sup<TAB>` to see completions like `super`, `supply`, `support`.

For a larger word list, install your system's dictionary:

```bash
# Arch
sudo pacman -S words

# Debian/Ubuntu
sudo apt install wamerican
```

The next `t completion` will include the system dictionary words (~100k+).
