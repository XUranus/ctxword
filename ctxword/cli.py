"""CLI entry point for ctxword - context-aware English vocabulary learning tool."""

import asyncio
import sys
from typing import Optional

import typer

from . import classify as classify_mod
from .config import load_config, Config
from .db import get_connection, init_db
from .errors import CtxwordError
from .lookup import lookup as do_lookup, get_history, get_lookup_detail
from .render import (
    render_lookup,
    render_lookup_json,
    render_typo_warning,
    render_history,
    render_review_card,
    render_review_answer,
    render_stats,
    console,
)
from .review import get_due_cards, rate_card, get_stats
from .anki import export_tsv, export_csv

# Known subcommand names (kept in sync with @app.command definitions)
_SUBCOMMANDS = {"review", "history", "show", "stats", "export", "classify-cmd", "clipboard-cmd"}

app = typer.Typer(
    name="t",
    help="Context-aware English vocabulary learning tool for programmers.",
    no_args_is_help=True,
)

# Global state
_config: Config | None = None
_conn = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = load_config()
    return _config


def get_db():
    global _conn
    if _conn is None:
        _conn = get_connection()
        init_db(_conn)
    return _conn


@app.command()
def lookup(
    query: str = typer.Argument(..., help="Word, phrase, or identifier to look up"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Surrounding context text"),
    force: bool = typer.Option(False, "--force", help="Force save even if suspected typo"),
    full: bool = typer.Option(False, "--full", help="Show full/detailed output"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_save: bool = typer.Option(False, "--no-save", help="Do not save this lookup"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Disable LLM processing (use local dictionary only)"),
    identifier: bool = typer.Option(False, "--identifier", help="Treat query as a code identifier"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Tags for the lookup (comma-separated)"),
    source: Optional[str] = typer.Option(None, "--source", help="Source of the query"),
):
    """Look up a word, phrase, or code identifier with LLM-powered explanation."""
    _do_lookup(
        query=query,
        config=get_config(),
        conn=get_db(),
        context=context,
        force=force,
        full=full,
        json_output=json_output,
        no_save=no_save,
        no_ai=no_ai,
        is_identifier=identifier,
    )


def _do_lookup(
    query: str,
    config: Config,
    conn,
    context: str | None = None,
    force: bool = False,
    full: bool = False,
    json_output: bool = False,
    no_save: bool = False,
    no_ai: bool = False,
    is_identifier: bool = False,
):
    try:
        result = asyncio.run(do_lookup(
            query=query,
            config=config,
            conn=conn,
            context=context,
            force=force,
            no_save=no_save,
            no_ai=no_ai,
            is_identifier=is_identifier,
        ))
    except CtxwordError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Handle typo
    if result.get("_typo"):
        render_typo_warning(query, result["_suggestion"], result.get("_suggestions", []))
        raise typer.Exit(1)

    if json_output:
        render_lookup_json(result)
    else:
        render_lookup(result, full=full)


@app.command()
def review(
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Max cards to review"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filter by tag"),
):
    """Review due vocabulary cards."""
    config = get_config()
    conn = get_db()

    cards = get_due_cards(conn, config, limit=limit)

    if not cards:
        console.print("[green]No cards due for review.[/green]")
        return

    total = len(cards)
    for i, card in enumerate(cards, 1):
        render_review_card(card, i, total)

        while True:
            key = typer.getchar()
            if key == "1":
                rating = "again"
                break
            elif key == "2":
                rating = "hard"
                break
            elif key == "3":
                rating = "good"
                break
            elif key == "4":
                rating = "easy"
                break
            elif key.lower() == "q":
                console.print("[dim]Review session ended.[/dim]")
                return
            else:
                console.print("[dim]Press 1-4 to rate, q to quit[/dim]")

        result = rate_card(conn, card["id"], rating)
        render_review_answer(card)
        console.print(
            f"[dim]Rated: {rating} | Next review: {result['new_due_at'][:10]}[/dim]\n"
        )

    console.print("[green]Review session complete![/green]")


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of entries to show"),
):
    """Show recent lookup history."""
    conn = get_db()
    rows = get_history(conn, limit=limit)

    if not rows:
        console.print("[dim]No lookups yet.[/dim]")
        return

    render_history(rows)


@app.command()
def show(
    query: str = typer.Argument(..., help="Query to show details for"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show saved details for a specific query."""
    conn = get_db()
    detail = get_lookup_detail(conn, query)

    if not detail:
        console.print(f"[red]No saved entry for '{query}'.[/red]")
        raise typer.Exit(1)

    if json_output:
        import json
        console.print(json.dumps(detail, ensure_ascii=False, indent=2, default=str))
    else:
        result = {
            "query": detail.get("query", query),
            "lemma": detail.get("lemma"),
            "part_of_speech": detail.get("part_of_speech"),
            "meaning_zh": detail.get("meaning_zh"),
            "meaning_en": detail.get("meaning_en"),
            "context_explanation": detail.get("context_explanation"),
            "technical_domain": detail.get("technical_domain"),
            "technical_note": detail.get("technical_note"),
            "collocations": detail.get("collocations"),
            "examples": detail.get("examples"),
            "common_mistakes": detail.get("common_mistakes"),
            "saved": True,
        }
        render_lookup(result, full=True)


@app.command()
def stats():
    """Show learning statistics."""
    conn = get_db()
    stats_data = get_stats(conn)
    render_stats(stats_data)


@app.command()
def export(
    target: str = typer.Argument("anki", help="Export target (currently: anki)"),
    output: str = typer.Option("ctxword_cards.tsv", "--output", "-o", help="Output file path"),
    format: str = typer.Option("tsv", "--format", "-f", help="Export format: tsv or csv"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filter cards by tag"),
):
    """Export review cards (e.g., to Anki-compatible format)."""
    if target != "anki":
        console.print(f"[red]Unknown export target: {target}. Currently only 'anki' is supported.[/red]")
        raise typer.Exit(1)

    conn = get_db()

    try:
        if format == "csv":
            count = export_csv(conn, output, tag_filter=tag)
        else:
            count = export_tsv(conn, output, tag_filter=tag)

        console.print(f"[green]Exported {count} cards to {output}[/green]")
    except CtxwordError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


@app.command(name="classify-cmd", hidden=True)
def classify_cmd(
    query: str = typer.Argument(..., help="Text to classify"),
):
    """Classify input type (word, phrase, identifier, etc.)."""
    from .classify import classify, split_identifier, InputType
    input_type = classify(query)
    words = split_identifier(query) if input_type == InputType.CODE_IDENTIFIER else []
    console.print(f"Query: [cyan]{query}[/cyan]")
    console.print(f"Type: [bold]{input_type.value}[/bold]")
    if words:
        console.print(f"Components: [dim]{', '.join(words)}[/dim]")


@app.command(name="clipboard-cmd", hidden=True)
def clipboard_cmd():
    """Read current clipboard content for use as context."""
    from .clipboard import read as clipboard_read
    try:
        clipboard_text = clipboard_read()
        console.print(f"[dim]Clipboard:[/dim] {clipboard_text[:200]}")
        console.print("[dim]Use this as context with:[/dim] t WORD -c \"TEXT\"")
    except CtxwordError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


def _parse_and_run(raw_args: list[str]) -> None:
    """Preprocess argv, reorder options, insert default 'lookup' command if needed."""
    if len(raw_args) <= 1 or (len(raw_args) == 2 and raw_args[1] in ("--help", "-h")):
        app(args=raw_args[1:], prog_name="t")
        return

    args = raw_args[1:]  # skip program name

    # If the first non-option arg is a known subcommand, run normally
    first_pos = None
    for a in args:
        if not a.startswith("-"):
            first_pos = a
            break

    if first_pos and first_pos in _SUBCOMMANDS:
        app(args=args)
        return

    # Check for --help or --clipboard or other global-only flags
    if "--help" in args or "-h" in args or "--clipboard" in args:
        app(args=args)
        return

    # No subcommand matched and not special flag -> treat as 'lookup' command
    # Reorder: move options before positional args
    options: list[str] = []
    positionals: list[str] = []
    value_opts = {"--context", "-c", "--tags", "--source", "--limit", "-n",
                  "--output", "-o", "--format", "-f", "--tag"}
    i = 0
    while i < len(args):
        token = args[i]
        if token.startswith("-"):
            options.append(token)
            if token in value_opts:
                i += 1
                if i < len(args):
                    options.append(args[i])
        else:
            positionals.append(token)
        i += 1

    final_args = ["lookup"] + options + positionals
    app(args=final_args)


def main_entry():
    """Entry point for console scripts."""
    try:
        _parse_and_run(sys.argv)
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted.[/dim]")
        sys.exit(0)
    except CtxwordError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main_entry()
