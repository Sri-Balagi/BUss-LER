from collections.abc import Callable
from typing import Any

from app.sdk.client.sync_client import BizOSClient
from app.shell.formatter import ShellFormatter


class ShellDispatcher:
    """
    Translates CLI commands into BizOSClient API calls.
    Preserves strict architectural boundaries (Shell -> SDK -> API).
    """

    def __init__(self, client: BizOSClient, formatter: ShellFormatter):
        self.client = client
        self.formatter = formatter
        self._commands: dict[str, Callable[..., Any]] = {}

    def register_command(self, name: str, handler: Callable[..., Any]) -> None:
        """Registers a handler for a specific shell command."""
        self._commands[name] = handler

    def dispatch(self, command: str, args: list[str]) -> int:
        """
        Executes a command and returns a standardized exit code.
        0 = Success
        1 = General Error
        2 = Auth/Config Error
        127 = Command Not Found
        """
        handler = self._commands.get(command)
        if not handler:
            self.formatter.print_error(f"Command not found: {command}")
            return 127

        try:
            return handler(self.client, self.formatter, args)
        except Exception as e:
            self.formatter.print_error(f"Execution failed: {command}", str(e))
            return 1
