# Product Requirements Document and Development Plan

# Project: ctxword

## 1. Product Summary

`ctxword` is a context-aware English vocabulary learning tool designed for Chinese-speaking programmers who frequently read technical documentation, code comments, error messages, issue discussions, and open-source project materials.

The product helps users move from passive lookup to active learning. Instead of simply translating a word, `ctxword` explains what the word or phrase means in a specific technical context, stores the lookup result, generates review cards, and schedules future review.

The initial product will be a Python-based command-line tool. Later versions will add KDE integration, clipboard-based lookup, desktop popup UI, and optional Anki integration.

## 2. Background and Problem Statement

Many programmers learning English frequently encounter unfamiliar words while reading:

- Technical documentation
- API references
- Error messages
- Git commit messages
- Pull request discussions
- Stack traces
- Open-source issue threads
- Code identifiers
- Terminal output

Traditional translation tools are fast, but they do not solve the full learning problem.

Common issues include:

1. **No context awareness**
   
   A word may have different meanings in different technical domains. For example, `race`, `panic`, `mount`, `resolve`, `reject`, `pending`, and `yield` all have special meanings in programming contexts.

2. **Poor support for phrases and collocations**
   
   Many important expressions are phrases, not single words: `race condition`, `breaking change`, `side effect`, `working tree`, `pull request`, `event loop`, `undefined behavior`.

3. **No morphology support**
   
   Learners may look up inflected forms such as `mounted`, `pending`, `resolved`, `panicked`, `indices`, `children`, or `written`, but they also need to understand the base form and related forms.

4. **No learning memory**
   
   Most lookup tools return an answer but do not store the result in a structured way for later review.

5. **No spaced repetition workflow**
   
   Lookup history rarely becomes review material automatically.

6. **No programmer-specific learning mode**
   
   General dictionaries and translators are not optimized for software engineering vocabulary, code identifiers, or technical documentation.

## 3. Product Vision

`ctxword` aims to become a lightweight personal English learning assistant for programmers.

The core vision is:

> Help programmers understand English words and phrases in real technical context, then convert those lookups into long-term memory.

The product should not try to replace full dictionaries, general translation tools, or Anki. Instead, it should connect these workflows:

```text
Encounter word in context
↓
Understand meaning in that context
↓
Save structured explanation
↓
Generate review cards
↓
Review over time
↓
Build technical English vocabulary
```

## 4. Target Users

### 4.1 Primary User

Chinese-speaking programmers who:

- Use Linux as their main development environment
- Read English technical documents regularly
- Want to improve technical English
- Prefer keyboard-driven tools
- Are comfortable with command-line workflows
- May use Arch Linux, KDE, terminal, editors, browsers, and documentation sites daily

### 4.2 Secondary Users

- Computer science students reading English documentation
- Open-source contributors reading GitHub issues and PRs
- Developers preparing for English technical interviews
- Engineers working with international teams
- Users who already use Anki but want better card generation from real context

## 5. Goals and Non-Goals

## 5.1 Goals

### G1. Context-aware lookup

The user can provide a target word or phrase plus surrounding context. The system explains the meaning of the target item within that context.

Example:

```bash
t pending --context "The promise is still pending."
```

Expected result:

- `pending` means the Promise has not been fulfilled or rejected yet
- It is common in async programming
- Related expressions: `pending request`, `pending transaction`, `pending changes`

### G2. Structured storage

Every lookup should be stored in a local database with:

- Original query
- Normalized form
- Context
- Explanation
- Technical notes
- Examples
- Generated review cards
- Timestamps
- Review state

### G3. Spelling and validity check

The tool should detect likely typos and avoid polluting the learning database with invalid words.

Example:

```bash
t enviroment
```

Expected behavior:

```text
Possible typo: enviroment
Did you mean: environment?
Use --force to save the original query.
```

### G4. Phrase and technical term support

The tool should support phrases and technical expressions, not just individual words.

Examples:

```bash
t "race condition"
t "breaking change"
t "working tree"
t "side effect"
```

### G5. Code identifier support

The tool should support programmer-specific identifiers such as:

```text
shouldInvalidateCache
getUserProfile
HTTPResponse
isMounted
race_condition
max_retry_count
```

The system should split identifiers and explain the meaning of important components.

### G6. Review system

The tool should generate review cards and provide a basic review command.

Example:

```bash
t review
```

The review system should support ratings:

```text
Again / Hard / Good / Easy
```

### G7. Anki export

The product should export review cards to Anki-compatible formats.

Possible export formats:

- CSV
- TSV
- AnkiConnect integration
- APKG in a later version

### G8. KDE-friendly workflow

The product should eventually support KDE-based lookup workflows:

- Global shortcut
- Clipboard lookup
- Popup result window
- Optional tray application

## 5.2 Non-Goals

The product should not attempt to become:

1. A full replacement for GoldenDict
2. A full machine translation product
3. A complete Anki replacement
4. A general-purpose OCR tool
5. A full desktop dictionary application in the MVP
6. A cloud-first vocabulary platform
7. A social learning application
8. A browser extension in the initial version

## 6. Product Principles

## 6.1 Context first

The product should prioritize contextual explanation over literal translation.

Bad output:

```text
panic = 恐慌
```

Good output:

```text
In Linux kernel context, panic means the kernel encountered an unrecoverable fatal error and stopped running.
```

## 6.2 Programmer-first explanations

When the context is technical, explanations should include technical meaning.

Example:

```text
resolve
```

In Promise context:

```text
resolve means to complete a Promise successfully.
```

In DNS context:

```text
resolve means to convert a domain name into an IP address.
```

In dependency management context:

```text
resolve means to determine the concrete version of a dependency.
```

## 6.3 Local-first storage

The user’s learning data should be stored locally by default.

Default locations:

```text
~/.local/share/ctxword/ctxword.db
~/.config/ctxword/config.toml
~/.cache/ctxword/
```

## 6.4 Cost-aware AI usage

LLM calls should be used only when they add meaningful value.

Recommended strategy:

- Use local dictionary and morphology tools first
- Use LLM for context-aware explanation
- Cache every LLM result
- Avoid repeated calls for identical query and context
- Allow users to disable LLM
- Support cheaper OpenAI-compatible APIs

## 6.5 Progressive enhancement

The product should work as a CLI first. GUI, KDE integration, OCR, and advanced review algorithms should be built later.

## 7. Core User Stories

## 7.1 Lookup a single word

As a user, I want to look up a single English word so that I can quickly understand its meaning.

Example:

```bash
t pending
```

Acceptance criteria:

- The tool returns Chinese meaning
- The tool returns English explanation
- The tool returns part of speech
- The tool stores the lookup
- The tool generates basic review cards if enabled

## 7.2 Lookup a word with context

As a user, I want to provide context so that I can understand the correct meaning of a word in a specific sentence.

Example:

```bash
t pending -c "The promise is still pending."
```

Acceptance criteria:

- The tool identifies the context-specific meaning
- The tool explains why the word has this meaning in context
- The tool marks technical domain if applicable
- The tool stores both query and context
- The tool generates context-based review cards

## 7.3 Lookup a phrase

As a user, I want to look up a phrase so that I can learn collocations and technical expressions.

Example:

```bash
t "race condition"
```

Acceptance criteria:

- The tool treats the input as a phrase
- The tool explains the phrase as a unit
- The tool does not simply translate each word separately
- The tool generates phrase-oriented review cards

## 7.4 Detect typo before saving

As a user, I want the tool to detect likely spelling mistakes so that wrong words are not saved to my learning database.

Example:

```bash
t enviroment
```

Acceptance criteria:

- The tool detects possible typo
- The tool suggests likely correction
- The tool does not save the typo by default
- The user can force saving with `--force`

## 7.5 Lookup from clipboard

As a user, I want to select and copy text, then invoke the tool to analyze it.

Example:

```bash
t --clipboard
```

Acceptance criteria:

- The tool reads clipboard content
- The user can choose or provide target word
- The tool uses clipboard text as context
- The result is saved

## 7.6 Review saved vocabulary

As a user, I want to review previously looked-up words so that I can remember them long term.

Example:

```bash
t review
```

Acceptance criteria:

- The tool shows due cards
- The user can rate each card
- The next due date is updated
- Review logs are stored

## 7.7 Export cards to Anki

As a user, I want to export my generated cards to Anki so that I can use Anki’s mature review ecosystem.

Example:

```bash
t export anki --format csv
```

Acceptance criteria:

- The tool exports cards in a valid format
- The exported cards include front, back, tags, and source context
- The output can be imported into Anki

## 7.8 Explain code identifiers

As a programmer, I want to understand English words inside code identifiers.

Example:

```bash
t shouldInvalidateCache --identifier
```

Acceptance criteria:

- The tool splits the identifier into words
- The tool explains the full identifier meaning
- The tool explains key vocabulary such as `invalidate`
- The tool saves the lookup as an identifier entry

## 8. Functional Requirements

## 8.1 CLI Interface

The CLI command should be named `t` or `ctxword`.

Primary command style:

```bash
t QUERY [OPTIONS]
```

### Required commands

```bash
t WORD
```

Lookup a single word.

```bash
t "PHRASE"
```

Lookup a phrase.

```bash
t WORD --context "TEXT"
```

Lookup a word with surrounding context.

```bash
t --clipboard
```

Read text from clipboard.

```bash
t review
```

Review due cards.

```bash
t history
```

Show recent lookups.

```bash
t show QUERY
```

Show saved details for a query.

```bash
t export anki
```

Export review cards.

```bash
t stats
```

Show learning statistics.

### Optional flags

```bash
--context, -c TEXT
--clipboard
--force
--full
--json
--no-save
--no-ai
--ai
--identifier
--tags TAGS
--source SOURCE
--limit N
```

## 8.2 Input Classification

The system should classify input as one of the following:

```text
single_word
phrase
sentence
code_identifier
mixed_text
unknown
```

Classification rules:

- Contains spaces and short length → likely phrase
- Contains camelCase, PascalCase, snake_case, kebab-case → code identifier
- Contains punctuation and multiple clauses → sentence or mixed text
- Single alphabetic token → single word
- Contains Chinese characters → Chinese input

## 8.3 Language Detection

The system should detect whether input is primarily:

```text
English
Chinese
Mixed
Unknown
```

MVP implementation can use simple heuristics:

- ASCII letters → English
- CJK characters → Chinese
- Both → Mixed

Later versions can use language detection libraries.

## 8.4 Spelling Check

The system should check whether a single English word is likely valid.

Possible tools:

- wordfreq
- wordninja
- wordnet
- wordfreq + word list
- wordfreq + rapidfuzz suggestions

MVP behavior:

- If word is unknown and close to a known word, warn user
- Do not save by default
- Allow `--force`

Example:

```text
Possible typo: enviroment
Suggested: environment
```

## 8.5 Morphology Analysis

For English words, the system should attempt to identify:

- Lemma
- Part of speech
- Inflected form
- Possible base form
- Common derived forms

Examples:

```text
resolved → resolve
mounted → mount
children → child
indices → index
running → run
panicked → panic
```

MVP may use lightweight tools. More advanced versions can use spaCy.

## 8.6 LLM Explanation

The system should call an LLM when:

- Context is provided
- Input is a phrase
- Input is a technical term
- Input is a code identifier
- User explicitly passes `--ai`

The system should avoid LLM calls when:

- Query is simple and no context is provided
- Cached result exists
- User passes `--no-ai`
- API key is unavailable

### LLM prompt requirements

The LLM should return structured JSON.

The explanation should include:

- Query
- Lemma
- Input type
- Part of speech
- Context-specific meaning in Chinese
- Context-specific meaning in English
- Technical domain
- Technical note
- Common collocations
- Example sentences
- Common mistakes
- Review cards

## 8.7 Output Rendering

Default output should be concise.

Example:

```text
pending
Meaning: 尚未完成 / 等待处理
Context: In async programming, a pending Promise has not been fulfilled or rejected yet.
Lemma: pending
Part of speech: adjective
Collocations: pending request, pending changes, pending promise
Saved: yes
Review: tomorrow
```

Detailed output should be available with:

```bash
t pending --full
```

JSON output should be available with:

```bash
t pending --json
```

## 8.8 Storage

The product should use SQLite for local storage.

Default path:

```text
~/.local/share/ctxword/ctxword.db
```

The database should store:

- Lookup history
- Entry explanation
- Review cards
- Review logs
- LLM cache
- Configuration metadata

## 8.9 Review System

MVP review system should support:

- Due cards
- Four ratings: Again, Hard, Good, Easy
- Simple scheduling intervals
- Review logs

MVP interval example:

```text
New + Again → 10 minutes or same day
New + Hard → 1 day
New + Good → 3 days
New + Easy → 7 days
Review + Again → 1 day
Review + Hard → previous interval × 1.2
Review + Good → previous interval × 2.5
Review + Easy → previous interval × 3.5
```

Later versions may support FSRS or delegate scheduling to Anki.

## 8.10 Anki Export

MVP export format:

```text
front	back	tags	source_context
```

Command:

```bash
t export anki --output cards.tsv
```

Later versions:

- AnkiConnect integration
- Deck selection
- Model selection
- Duplicate detection
- Media support

## 8.11 KDE Integration

KDE integration should be developed after CLI MVP.

Recommended stages:

### Stage 1: Clipboard workflow

User selects text, copies it, then triggers:

```bash
t --clipboard
```

### Stage 2: Global shortcut

Bind KDE global shortcut to:

```bash
ctxword-popup --clipboard
```

### Stage 3: Popup UI

A lightweight popup displays:

- Target word
- Context meaning
- Technical note
- Save status
- Review card count

### Stage 4: Tray app

Optional tray app for:

- Quick lookup
- Review reminder
- Settings
- Recent lookups

## 9. Non-Functional Requirements

## 9.1 Performance

Expected performance goals:

- Local lookup should return within 300 ms
- Cached AI result should return within 300 ms
- Fresh LLM lookup should stream or show progress
- CLI startup time should remain under 500 ms if possible

## 9.2 Reliability

The tool should handle:

- Missing API key
- Network failure
- Invalid LLM JSON
- Empty clipboard
- Invalid query
- Database migration failure
- Interrupted review session

## 9.3 Privacy

Local-first by default.

The system should clearly separate:

- Local processing
- Data sent to LLM API
- Stored history

The user should be able to disable remote AI calls:

```bash
t --no-ai
```

Config option:

```toml
[llm]
enabled = false
```

## 9.4 Cost Control

The system should reduce API usage through:

- Query cache
- Context hash
- Local dictionary fallback
- Batch processing
- Optional model selection
- Token limit control

Example config:

```toml
[llm]
provider = "openai_compatible"
base_url = "https://api.example.com/v1"
model = "cheap-model"
max_tokens = 1200
temperature = 0.2
```

## 9.5 Portability

MVP should support:

- Arch Linux
- Python 3.11+
- Terminal workflow

Later versions may support:

- Other Linux distributions
- macOS
- Windows

## 10. System Architecture

## 10.1 High-Level Architecture

```text
CLI / Clipboard / KDE Popup
          ↓
Input Classifier
          ↓
Language Detector
          ↓
Morphology Analyzer
          ↓
Dictionary / Cache Layer
          ↓
LLM Explanation Layer
          ↓
Structured Result Validator
          ↓
SQLite Storage
          ↓
Renderer / Review / Export
```

## 10.2 Module Structure

Recommended Python package structure:

```text
ctxword/
  pyproject.toml
  README.md
  docs/
    PRD.md
    ARCHITECTURE.md
    PROMPTS.md
  ctxword/
    __init__.py
    cli.py
    config.py
    paths.py
    db.py
    migrations.py
    models.py
    classify.py
    language.py
    spelling.py
    morphology.py
    dictionary.py
    llm.py
    cache.py
    lookup.py
    review.py
    anki.py
    clipboard.py
    identifier.py
    render.py
    errors.py
    prompts/
      explain_word.md
      explain_phrase.md
      explain_identifier.md
  tests/
    test_classify.py
    test_identifier.py
    test_spelling.py
    test_review.py
    test_models.py
```

## 10.3 Recommended Dependencies

MVP dependencies:

```text
typer
rich
pydantic
httpx
sqlite-utils or built-in sqlite3
platformdirs
rapidfuzz
python-dotenv or tomli/tomllib
pyperclip or custom clipboard adapter
```

Optional dependencies:

```text
wordfreq
wordninja
nltk
spacy
textual
PySide6
```

## 11. Data Model

## 11.1 lookup table

Stores every user lookup operation.

```sql
CREATE TABLE lookup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    normalized_query TEXT,
    input_type TEXT NOT NULL,
    language TEXT,
    context TEXT,
    context_hash TEXT,
    source TEXT,
    status TEXT NOT NULL DEFAULT 'saved',
    created_at TEXT NOT NULL
);
```

Possible `input_type` values:

```text
single_word
phrase
sentence
code_identifier
mixed_text
unknown
```

Possible `status` values:

```text
saved
not_saved
suspected_typo
forced
cached
```

## 11.2 entry table

Stores structured explanation result.

```sql
CREATE TABLE entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lookup_id INTEGER NOT NULL,
    lemma TEXT,
    part_of_speech TEXT,
    meaning_zh TEXT,
    meaning_en TEXT,
    context_explanation TEXT,
    technical_domain TEXT,
    technical_note TEXT,
    collocations TEXT,
    examples TEXT,
    common_mistakes TEXT,
    raw_response TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (lookup_id) REFERENCES lookup(id)
);
```

JSON fields stored as text:

- `part_of_speech`
- `technical_domain`
- `collocations`
- `examples`
- `common_mistakes`

## 11.3 review_card table

Stores generated cards.

```sql
CREATE TABLE review_card (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    card_type TEXT NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    tags TEXT,
    due_at TEXT,
    interval_days REAL DEFAULT 0,
    ease REAL DEFAULT 2.5,
    reps INTEGER DEFAULT 0,
    lapses INTEGER DEFAULT 0,
    state TEXT DEFAULT 'new',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (entry_id) REFERENCES entry(id)
);
```

Possible `card_type` values:

```text
meaning
context
phrase
collocation
technical_term
identifier
morphology
cloze
```

## 11.4 review_log table

Stores review events.

```sql
CREATE TABLE review_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    rating TEXT NOT NULL,
    reviewed_at TEXT NOT NULL,
    elapsed_ms INTEGER,
    old_due_at TEXT,
    new_due_at TEXT,
    old_interval_days REAL,
    new_interval_days REAL,
    FOREIGN KEY (card_id) REFERENCES review_card(id)
);
```

Possible `rating` values:

```text
again
hard
good
easy
```

## 11.5 llm_cache table

Caches LLM results.

```sql
CREATE TABLE llm_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT NOT NULL UNIQUE,
    query TEXT NOT NULL,
    context_hash TEXT,
    model TEXT,
    prompt_version TEXT,
    response_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

Cache key formula:

```text
sha256(query + context_hash + model + prompt_version)
```

## 12. LLM JSON Schema

The LLM should return JSON matching this structure:

```json
{
  "query": "pending",
  "normalized_query": "pending",
  "input_type": "single_word",
  "lemma": "pending",
  "part_of_speech": ["adjective"],
  "meaning_zh": "尚未完成；等待处理",
  "meaning_en": "not yet completed, decided, or resolved",
  "context_explanation": "In this sentence, pending describes a Promise that has not been fulfilled or rejected yet.",
  "technical_domain": ["programming", "async"],
  "technical_note": "In async programming, a Promise can be pending, fulfilled, or rejected.",
  "collocations": [
    "pending request",
    "pending changes",
    "pending promise",
    "pending transaction"
  ],
  "examples": [
    {
      "en": "The request is still pending.",
      "zh": "这个请求仍在等待处理。"
    },
    {
      "en": "The promise remains pending until the network call completes.",
      "zh": "在网络调用完成之前，这个 Promise 会一直处于 pending 状态。"
    }
  ],
  "common_mistakes": [
    "Do not translate pending promise literally as 承诺待定. In programming, Promise is a technical object."
  ],
  "cards": [
    {
      "type": "context",
      "front": "In async programming, what does a pending Promise mean?",
      "back": "It means the Promise has not been fulfilled or rejected yet.",
      "tags": ["async", "promise", "programming"]
    }
  ]
}
```

## 13. Prompt Design

## 13.1 System Prompt

```text
You are an English learning assistant for Chinese-speaking programmers.
Your job is to explain English words, phrases, and code identifiers in technical context.
Do not only translate. Explain the actual meaning in the given context.
Prefer concise, accurate, programmer-friendly explanations.
Return valid JSON only.
```

## 13.2 User Prompt Template

```text
Target: {query}
Input type: {input_type}
Context: {context}
User language: Chinese

Please analyze the target item and return JSON with:
- normalized query
- lemma
- part of speech
- Chinese meaning
- English meaning
- context-specific explanation
- technical domain if any
- technical note if useful
- common collocations
- example sentences
- common mistakes
- review cards
```

## 13.3 Prompt Versioning

Prompts should have version IDs.

Example:

```text
explain_word_v1
explain_phrase_v1
explain_identifier_v1
```

Prompt version should be stored in `llm_cache` for reproducibility.

## 14. Review Card Strategy

## 14.1 Card Types

### Meaning card

```text
Front: What does "pending" mean?
Back: 尚未完成；等待处理
```

### Context card

```text
Front: In "The promise is still pending", what does pending mean?
Back: The Promise has not been fulfilled or rejected yet.
```

### Collocation card

```text
Front: Complete the phrase: pending ___
Back: request / changes / promise / transaction
```

### Technical term card

```text
Front: What does "race" mean in "race condition"?
Back: A situation where behavior depends on timing or ordering of concurrent operations.
```

### Identifier card

```text
Front: What does shouldInvalidateCache mean?
Back: It means whether the cache should be made invalid or cleared.
```

### Morphology card

```text
Front: What is the base form of "mounted"?
Back: mount
```

## 14.2 Card Generation Rules

MVP should generate at most 3 cards per lookup by default.

Recommended priority:

1. Context card if context exists
2. Technical term card if technical domain exists
3. Meaning card
4. Collocation card
5. Morphology card

Avoid generating too many cards for simple lookups.

## 15. CLI UX Design

## 15.1 Default lookup output

```text
$ t pending -c "The promise is still pending."

pending
Meaning: 尚未完成 / 等待处理
Context: In async programming, a pending Promise has not been fulfilled or rejected yet.
Lemma: pending
POS: adjective
Domain: programming, async
Collocations: pending request, pending changes, pending promise
Cards: 2 created
Saved: yes
```

## 15.2 Typo output

```text
$ t enviroment

Possible typo: enviroment
Suggested correction: environment

Run:
  t environment

Or save anyway:
  t enviroment --force
```

## 15.3 Review output

```text
$ t review

Card 1/12

Q: In async programming, what does a pending Promise mean?

[1] Again  [2] Hard  [3] Good  [4] Easy  [q] Quit
> 3

Saved. Next review: 2026-05-01
```

## 15.4 History output

```text
$ t history

2026-04-28  pending           programming, async
2026-04-28  race condition    concurrency
2026-04-27  invalidate        cache
2026-04-27  working tree      git
```

## 16. Configuration

Default config path:

```text
~/.config/ctxword/config.toml
```

Example:

```toml
[general]
language = "zh-CN"
auto_save = true
max_cards_per_lookup = 3

[storage]
database_path = "~/.local/share/ctxword/ctxword.db"

[llm]
enabled = true
provider = "openai_compatible"
base_url = "https://api.example.com/v1"
api_key_env = "CTXWORD_API_KEY"
model = "cheap-model"
temperature = 0.2
max_tokens = 1200
cache = true

[review]
enabled = true
scheduler = "simple"
new_cards_per_day = 20
review_cards_per_day = 100

[clipboard]
backend = "auto"

[anki]
enabled = false
default_deck = "ctxword"
export_format = "tsv"
```

## 17. Development Plan

## 17.1 Phase 0: Project Setup

Estimated scope: 1–2 days

### Tasks

- Create Python project using `pyproject.toml`
- Add CLI entry point
- Add formatting and linting
- Add test framework
- Add basic README
- Add config path handling
- Add database path handling

### Deliverables

- Installable local package
- `ctxword --help`
- `t --help` alias if desired
- Basic project documentation

### Acceptance criteria

```bash
pipx install -e .
t --help
```

works locally.

## 17.2 Phase 1: Basic CLI Lookup

Estimated scope: 3–5 days

### Tasks

- Implement CLI command parsing
- Implement input classification
- Implement language detection heuristic
- Implement basic local dictionary fallback or placeholder explanation
- Implement Rich output rendering
- Implement SQLite initialization
- Store lookup records

### Deliverables

Commands:

```bash
t pending
t "race condition"
t history
```

### Acceptance criteria

- Query is parsed correctly
- Phrase input works
- Lookup is saved to SQLite
- History command shows saved records

## 17.3 Phase 2: Spelling and Morphology

Estimated scope: 3–6 days

### Tasks

- Add spelling validity check
- Add typo suggestion using rapidfuzz
- Add `--force`
- Add morphology analyzer
- Store lemma and part of speech when available
- Add tests for common inflections

### Deliverables

```bash
t enviroment
t mounted
t running
t indices
```

### Acceptance criteria

- Obvious typos are detected
- Valid words are not blocked
- Lemmas are extracted for common forms
- Forced save works

## 17.4 Phase 3: LLM Integration

Estimated scope: 5–8 days

### Tasks

- Add OpenAI-compatible API client
- Add config for provider/model/API key
- Design prompt templates
- Add Pydantic schema for LLM response
- Validate JSON output
- Add retry and error handling
- Add cache table
- Add context hash
- Store structured entry results

### Deliverables

```bash
t pending -c "The promise is still pending."
t "race condition"
t shouldInvalidateCache --identifier
```

### Acceptance criteria

- LLM result is parsed as structured JSON
- Invalid JSON is handled gracefully
- Cached lookup avoids repeated API call
- Result is saved in database
- `--no-ai` disables remote call

## 17.5 Phase 4: Review Card Generation

Estimated scope: 4–7 days

### Tasks

- Generate cards from LLM result
- Store cards in `review_card`
- Implement due card query
- Implement review CLI
- Implement simple scheduler
- Store review logs
- Add `stats` command

### Deliverables

```bash
t review
t stats
```

### Acceptance criteria

- Cards are generated after lookup
- Due cards appear in review
- User rating updates next due date
- Review logs are saved

## 17.6 Phase 5: Anki Export

Estimated scope: 2–4 days

### Tasks

- Export cards as TSV
- Add tags
- Include source context
- Add duplicate filtering
- Add command options

### Deliverables

```bash
t export anki --output ctxword_cards.tsv
```

### Acceptance criteria

- TSV can be imported into Anki
- Cards contain front/back/tags/context
- Export does not duplicate already exported cards if tracking is enabled

## 17.7 Phase 6: Clipboard Workflow

Estimated scope: 2–5 days

### Tasks

- Implement clipboard backend
- Support wl-paste
- Support xclip or xsel fallback
- Add `--clipboard`
- If clipboard contains multiple words, prompt user for target word
- Save clipboard content as context

### Deliverables

```bash
t --clipboard
t pending --clipboard
```

### Acceptance criteria

- Clipboard text is read correctly
- User can choose target word
- Clipboard text is used as context

## 17.8 Phase 7: KDE Integration MVP

Estimated scope: 5–10 days

### Tasks

- Create `ctxword-popup`
- Display result in a small popup window
- Support clipboard lookup
- Add KDE shortcut setup documentation
- Optional: create `.desktop` file

### Deliverables

```bash
ctxword-popup --clipboard
```

### Acceptance criteria

- User can bind command to KDE global shortcut
- Popup displays lookup result
- Lookup is saved to same database as CLI

## 17.9 Phase 8: Advanced Features

Future work.

Possible features:

- AnkiConnect integration
- FSRS-compatible scheduling
- Textual TUI
- PySide6 desktop app
- Browser extension
- OCR-based screen selection
- Sync across devices
- Import old `en.dic` and `ch.dic`
- Batch lookup from documents
- Git commit / issue vocabulary mode
- Code identifier batch extraction from source files

## 18. MVP Scope

## 18.1 MVP Must-Have

- Python CLI
- Single word lookup
- Phrase lookup
- Context lookup
- SQLite storage
- LLM JSON explanation
- Cache
- Typo detection
- Basic morphology
- Review card generation
- Simple review command
- Anki TSV export

## 18.2 MVP Should-Have

- Clipboard lookup
- Identifier support
- Rich output
- Config file
- History command
- Stats command

## 18.3 MVP Could-Have

- KDE popup
- AnkiConnect
- TUI
- Multiple LLM providers
- Import old dictionary files

## 18.4 MVP Will-Not-Have

- OCR screen capture
- Full GUI
- Cloud sync
- Mobile app
- Browser extension
- Full FSRS implementation

## 19. Risks and Mitigations

## 19.1 Risk: Rebuilding existing dictionary tools

### Problem

GoldenDict, translate-shell, and online dictionaries already solve basic lookup.

### Mitigation

Focus on:

- Context explanation
- Programmer vocabulary
- Review card generation
- Code identifiers
- Local learning history

## 19.2 Risk: LLM cost grows too fast

### Problem

Calling LLM on every lookup may become expensive.

### Mitigation

- Cache aggressively
- Use local tools first
- Only use LLM for context, phrases, and technical terms
- Add `--no-ai`
- Support cheap models
- Limit max tokens

## 19.3 Risk: LLM hallucination

### Problem

LLM may produce incorrect explanations.

### Mitigation

- Prefer context-grounded prompts
- Use structured JSON
- Show confidence or warning for uncertain results
- Keep raw context visible
- Optionally compare with local dictionary results

## 19.4 Risk: KDE / Wayland complexity

### Problem

Screen selection, global shortcuts, and clipboard access may behave differently under Wayland and X11.

### Mitigation

- Start with clipboard workflow
- Document Wayland limitations
- Avoid OCR in MVP
- Provide manual command workflow first

## 19.5 Risk: Review system becomes too complex

### Problem

Spaced repetition algorithms can become a large project.

### Mitigation

- Use simple scheduler first
- Export to Anki
- Add FSRS later only if needed

## 19.6 Risk: Too much output hurts CLI UX

### Problem

Long explanations are hard to read in terminal.

### Mitigation

- Concise output by default
- `--full` for details
- `--json` for machine-readable output
- Limit default card count

## 20. Success Metrics

## 20.1 Usage Metrics

- Number of lookups per day
- Number of context lookups per day
- Number of generated cards
- Number of reviewed cards
- Review completion rate

## 20.2 Learning Metrics

- Cards remembered after 7 days
- Cards remembered after 30 days
- Percentage of repeated lookup words
- Reduction in repeated lookups over time

## 20.3 Product Quality Metrics

- LLM cache hit rate
- Average lookup latency
- API cost per 100 lookups
- Typo false positive rate
- JSON parse failure rate

## 21. Testing Plan

## 21.1 Unit Tests

Test modules:

- Input classification
- Language detection
- Identifier splitting
- Spelling suggestions
- Morphology rules
- Review scheduler
- Cache key generation
- Database operations

## 21.2 Integration Tests

Scenarios:

- Lookup word and save
- Lookup phrase and save
- Lookup with context and LLM mock
- Generate cards
- Review cards
- Export TSV
- Load config

## 21.3 Manual Tests

Manual workflows:

```bash
t pending
t pending -c "The promise is still pending."
t "race condition"
t shouldInvalidateCache --identifier
t enviroment
t review
t export anki
```

## 22. Migration from Existing Script

The user currently has files like:

```text
en.dic
ch.dic
```

Migration command:

```bash
t import legacy --en path/to/en.dic --ch path/to/ch.dic
```

Behavior:

- Import each line as a lookup
- Mark source as `legacy`
- Do not call LLM by default
- Optionally enrich imported entries later

Command:

```bash
t enrich --source legacy --limit 50
```

## 23. Example End-to-End Flow

User reads this sentence:

```text
The promise remains pending until the network request resolves.
```

User runs:

```bash
t pending -c "The promise remains pending until the network request resolves."
```

System:

1. Classifies `pending` as single word
2. Detects English
3. Checks spelling
4. Finds lemma
5. Computes context hash
6. Checks cache
7. Calls LLM if cache miss
8. Validates JSON response
9. Saves lookup and entry
10. Generates cards
11. Renders concise result

Output:

```text
pending
Meaning: 尚未完成 / 等待处理
Context: Here it describes a Promise that has not resolved or rejected yet.
Domain: programming, async
Collocations: pending promise, pending request, pending transaction
Cards: 2 created
Saved: yes
```

Generated card:

```text
Front: In async programming, what does a pending Promise mean?
Back: It means the Promise has not been fulfilled or rejected yet.
```

## 24. Recommended Implementation Order

The best implementation order is:

```text
1. Project setup
2. CLI skeleton
3. SQLite storage
4. Input classification
5. History command
6. Spelling check
7. Morphology
8. LLM client
9. JSON schema validation
10. Cache
11. Card generation
12. Review command
13. Anki export
14. Clipboard support
15. KDE popup
```

This order avoids spending early time on KDE, OCR, or GUI complexity before the core learning loop is proven.

## 25. Initial GitHub Issues

Suggested first issues:

1. Initialize Python package and CLI entry point
2. Add config and path management
3. Add SQLite schema and migrations
4. Implement input classifier
5. Implement history command
6. Add spelling suggestion module
7. Add morphology module
8. Add OpenAI-compatible LLM client
9. Add prompt templates and response schema
10. Add LLM cache
11. Add review card generation
12. Add review command
13. Add Anki TSV export
14. Add clipboard support
15. Add legacy import from `en.dic` and `ch.dic`

## 26. Recommended First Milestone

The first meaningful milestone should be:

> `ctxword` can look up a word or phrase with context, save the structured result locally, and generate at least one review card.

Milestone demo:

```bash
t pending -c "The promise is still pending."
t history
t review
```

This proves the full core loop:

```text
lookup → understand → save → review
```

## 27. Final Product Positioning

`ctxword` should be positioned as:

> A context-aware technical English learning tool for programmers.

It is not just a translator.
It is not just a dictionary.
It is not just an Anki card generator.

Its core value is connecting real reading context with long-term vocabulary learning.

