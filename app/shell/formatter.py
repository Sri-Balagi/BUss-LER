import json
from typing import Any

from rich.console import Console
from rich.table import Table


class ShellFormatter:
    """
    Handles formatting of BizShell output.
    Supports Rich visual formatting for REPL and raw JSON for scripting/CI.
    """

    def __init__(self, use_json: bool = False):
        self.use_json = use_json
        self.console = Console()

    def print_success(self, message: str, data: Any = None) -> None:
        if self.use_json:
            output = {"status": "success", "message": message}
            if data is not None:
                output["data"] = data
            print(json.dumps(output))
        else:
            self.console.print(f"[bold green]SUCCESS:[/bold green] {message}")
            if data:
                self.console.print(data)

    def print_error(self, message: str, details: Any = None) -> None:
        if self.use_json:
            output = {"status": "error", "message": message}
            if details is not None:
                output["details"] = details
            print(json.dumps(output))
        else:
            self.console.print(f"[bold red]ERROR:[/bold red] {message}")
            if details:
                self.console.print(f"[red]{details}[/red]")

    def print_table(self, title: str, columns: list[str], rows: list[list[Any]]) -> None:
        if self.use_json:
            output = {"title": title, "columns": columns, "rows": rows}
            print(json.dumps(output))
        else:
            table = Table(title=title)
            for col in columns:
                table.add_column(col)
            for row in rows:
                table.add_row(*[str(item) for item in row])
            self.console.print(table)
