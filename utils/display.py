"""Rich table rendering shared by CLI commands."""

from rich.console import Console
from rich.table import Table


def render_table(console: Console, title: str, columns: list[str], rows: list[list[str]]) -> None:
    """Render rows in a consistently styled Rich table."""
    if not rows:
        console.print(f"No {title.lower()} found.")
        return
    table = Table(title=title, header_style="bold cyan")
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*row)
    console.print(table)