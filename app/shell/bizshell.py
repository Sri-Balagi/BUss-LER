import argparse
import cmd
import sys

from app.sdk.client.config import SDKConfig
from app.sdk.client.sync_client import BizOSClient
from app.shell.dispatcher import ShellDispatcher
from app.shell.formatter import ShellFormatter


class BizShell(cmd.Cmd):
    """
    Main entry point for the BizOS Shell.
    Supports interactive REPL and non-interactive script execution.
    """
    prompt = "bizos> "

    def __init__(self, use_json: bool = False, config: SDKConfig | None = None):
        super().__init__()
        self.formatter = ShellFormatter(use_json=use_json)
        self.client = BizOSClient(config=config)
        self.dispatcher = ShellDispatcher(self.client, self.formatter)
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        from app.shell.commands.devex_cmds import register_devex_commands
        from app.shell.commands.registry_cmds import register_registry_commands
        from app.shell.commands.status_cmds import register_status_commands
        from app.shell.commands.workflow_cmds import register_workflow_commands

        register_registry_commands(self.dispatcher)
        register_workflow_commands(self.dispatcher)
        register_status_commands(self.dispatcher)
        register_devex_commands(self.dispatcher)

    def execute_command(self, command_line: str) -> int:
        """Parses and executes a single command string via dispatcher."""
        parts = command_line.strip().split()
        if not parts:
            return 0
        command = parts[0]
        args = parts[1:]

        if command in ("exit", "quit"):
            sys.exit(0)
        elif command == "help":
            self.do_help(" ".join(args))
            return 0

        return self.dispatcher.dispatch(command, args)

    def default(self, line: str) -> bool:
        """Called on an input line when the command prefix is not recognized."""
        if line == "EOF":
            print()
            sys.exit(0)
        self.execute_command(line)
        return False

    def do_exit(self, arg: str) -> bool:
        """Exit the shell."""
        sys.exit(0)

    def do_quit(self, arg: str) -> bool:
        """Exit the shell."""
        sys.exit(0)

    # Dynamic dispatch for recognized commands to allow tab completion / help
    def do_status(self, arg: str) -> None:
        """Show system status."""
        self.execute_command(f"status {arg}")

    def do_ps(self, arg: str) -> None:
        """List active workflows."""
        self.execute_command(f"ps {arg}")

    def do_kill(self, arg: str) -> None:
        """Kill a running workflow or process."""
        self.execute_command(f"kill {arg}")

    def do_memory(self, arg: str) -> None:
        """Display memory/context information."""
        self.execute_command(f"memory {arg}")

    def do_registry(self, arg: str) -> None:
        """Manage system registries (e.g. registry list)."""
        self.execute_command(f"registry {arg}")



    def do_workflow(self, arg: str) -> None:
        """Manage workflows."""
        self.execute_command(f"workflow {arg}")

    def help_create_app(self) -> None:
        """Scaffold a new BizOS App. Usage: create-app <name>"""
        self.formatter.console.print("Scaffold a new BizOS App. Usage: create-app <name>")

    def help_create_plugin(self) -> None:
        """Scaffold a new BizOS Plugin. Usage: create-plugin <name>"""
        self.formatter.console.print("Scaffold a new BizOS Plugin. Usage: create-plugin <name>")

    def emptyline(self) -> bool:
        """Do nothing on empty input line."""
        return False

    def run_repl(self) -> None:
        """Runs the interactive Read-Eval-Print-Loop."""
        self.formatter.console.print("[bold cyan]Welcome to BizShell (BizOS v6.0.0)[/bold cyan]")
        self.formatter.console.print("Type 'help' for a list of commands, or 'exit' to quit.\n")
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print()
            sys.exit(0)

    def run_script(self, filepath: str) -> int:
        """Executes commands from a script file."""
        try:
            with open(filepath) as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    exit_code = self.execute_command(line)
                    if exit_code != 0:
                        return exit_code
            return 0
        except Exception as e:
            self.formatter.print_error(f"Failed to run script: {filepath}", str(e))
            return 1


def main():
    parser = argparse.ArgumentParser(description="BizOS Shell")
    parser.add_argument("script", nargs="?", help="Optional script file to execute")
    parser.add_argument("--json", action="store_true", help="Output in machine-readable JSON format")

    args = parser.parse_args()

    shell = BizShell(use_json=args.json)

    if args.script:
        sys.exit(shell.run_script(args.script))
    else:
        shell.run_repl()

if __name__ == "__main__":
    main()
