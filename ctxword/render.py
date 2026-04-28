"""Output rendering using Rich."""

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def _format_list(data: Any) -> str:
    """Format a list or JSON string into a readable string."""
    if data is None:
        return ""
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            if isinstance(parsed, list):
                return ", ".join(str(item) for item in parsed)
        except (json.JSONDecodeError, TypeError):
            return data
    if isinstance(data, list):
        return ", ".join(str(item) for item in data)
    return str(data)


def render_lookup(result: dict, full: bool = False) -> None:
    """Render a single lookup result."""
    query = result.get("query", "")
    meaning_zh = result.get("meaning_zh") or _format_list(result.get("meaning_zh"))
    meaning_en = result.get("meaning_en", "")
    lemma = result.get("lemma", "")
    pos = _format_list(result.get("part_of_speech", []))
    domain = _format_list(result.get("technical_domain", []))
    collocations = _format_list(result.get("collocations", []))
    context_explanation = result.get("context_explanation", "")
    tech_note = result.get("technical_note", "")
    saved = result.get("saved", False)
    card_count = result.get("card_count", 0)

    # Build output text
    lines: list[tuple[str, str, str]] = []  # (label, value, style)

    lines.append(("", query, "bold cyan"))

    if meaning_zh:
        lines.append(("Meaning", meaning_zh, "green"))
    if meaning_en:
        lines.append(("EN", meaning_en, "dim"))

    if lemma and lemma != query.lower():
        lines.append(("Lemma", lemma, "yellow"))
    if pos:
        lines.append(("POS", pos, "dim"))
    if domain:
        lines.append(("Domain", domain, "blue"))
    if context_explanation:
        lines.append(("Context", context_explanation, "white"))
    if tech_note and full:
        lines.append(("Tech note", tech_note, "yellow"))
    if collocations:
        lines.append(("Collocations", collocations, "dim"))

    if full:
        examples = result.get("examples", "")
        if examples:
            lines.append(("Examples", _format_list(examples), "dim"))
        mistakes = result.get("common_mistakes", "")
        if mistakes:
            lines.append(("Common mistakes", _format_list(mistakes), "red"))

    if card_count:
        lines.append(("Cards", f"{card_count} created", "magenta"))

    if saved:
        lines.append(("Saved", "yes", "green"))

    for label, value, style in lines:
        if label:
            console.print(f"[bold]{label}:[/bold] [{style}]{value}[/{style}]")
        else:
            console.print(f"[{style}]{value}[/{style}]")


def render_lookup_json(result: dict) -> None:
    """Render result as JSON."""
    # Remove internal fields
    output = {k: v for k, v in result.items() if not k.startswith("_")}
    console.print(json.dumps(output, ensure_ascii=False, indent=2))


def render_typo_warning(query: str, suggestion: str, suggestions: list) -> None:
    """Render a typo warning."""
    console.print(f"\n[yellow]Possible typo:[/yellow] [bold red]{query}[/bold red]")
    console.print(f"[green]Suggested correction:[/green] [bold]{suggestion}[/bold]")

    if len(suggestions) > 1:
        alt = ", ".join(s[0] for s in suggestions[1:])
        console.print(f"[dim]Other suggestions: {alt}[/dim]")

    console.print(f"\nRun:\n  [bold]t {suggestion}[/bold]")
    console.print(f"\nOr save anyway:\n  [bold]t {query} --force[/bold]")


def render_history(rows: list) -> None:
    """Render lookup history as a table."""
    table = Table(title="Lookup History")
    table.add_column("Date", style="dim")
    table.add_column("Query", style="cyan")
    table.add_column("Type", style="dim")
    table.add_column("Domain", style="blue")
    table.add_column("Status", style="green")

    for row in rows:
        table.add_row(
            row.get("created_at", "")[:10] if row.get("created_at") else "",
            row.get("query", ""),
            row.get("input_type", ""),
            _format_list(row.get("technical_domain", "")),
            row.get("status", ""),
        )

    console.print(table)


def render_review_card(card: dict, current: int, total: int) -> None:
    """Render a review card."""
    console.clear()
    console.print(f"\n[dim]Card {current}/{total}[/dim]\n")
    console.print(Panel(
        f"[bold white]{card['front']}[/bold white]",
        title="Question",
        border_style="cyan",
    ))
    console.print("\n[1] Again  [2] Hard  [3] Good  [4] Easy  [q] Quit")


def render_review_answer(card: dict) -> None:
    """Show the answer after rating."""
    console.print(f"\n[green]Answer:[/green] {card['back']}")


def render_stats(stats: dict) -> None:
    """Render learning statistics."""
    table = Table(title="Learning Stats")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="cyan")

    table.add_row("Total lookups", str(stats.get("total_lookups", 0)))
    table.add_row("Total cards", str(stats.get("total_cards", 0)))
    table.add_row("Due cards", str(stats.get("due_cards", 0)))
    table.add_row("New cards", str(stats.get("new_cards", 0)))
    table.add_row("Learning cards", str(stats.get("learning_cards", 0)))
    table.add_row("Mature cards", str(stats.get("mature_cards", 0)))
    table.add_row("Reviews today", str(stats.get("reviews_today", 0)))
    table.add_row("Cache hit rate", f"{stats.get('cache_hit_rate', 0):.0%}")

    console.print(table)
