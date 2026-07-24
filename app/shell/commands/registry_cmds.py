
from app.sdk.client.sync_client import BizOSClient
from app.shell.dispatcher import ShellDispatcher
from app.shell.formatter import ShellFormatter


def handle_registry(client: BizOSClient, formatter: ShellFormatter, args: list[str]) -> int:
    """Manage registries. Usage: registry list <registry_name>"""
    if not args:
        formatter.print_error("Missing subcommand. Usage: registry list <registry_name>")
        return 1

    subcommand = args[0]
    sub_args = args[1:]

    if subcommand == "list":
        return handle_ls_registry(client, formatter, sub_args)
    else:
        formatter.print_error(f"Unknown registry subcommand: {subcommand}")
        return 1

def handle_ls_registry(client: BizOSClient, formatter: ShellFormatter, args: list[str]) -> int:
    """Lists items in a specific registry. Usage: registry list <registry_name>"""
    if not args:
        formatter.print_error("Missing registry name. Usage: registry list <registry_name>")
        return 1

    registry_name = args[0]

    try:
        items = client.list_registry_items(registry_name)

        if not items:
            formatter.print_success(f"Registry '{registry_name}' is empty.")
            return 0

        columns = ["ID", "Name", "Type"]
        rows = [[getattr(item, "id", "N/A"), getattr(item, "name", "N/A"), getattr(item, "type", "N/A")] for item in items]

        formatter.print_table(f"Registry: {registry_name}", columns, rows)
        return 0

    except Exception as e:
        formatter.print_error(f"Failed to list registry '{registry_name}'", str(e))
        return 1

def register_registry_commands(dispatcher: ShellDispatcher) -> None:
    dispatcher.register_command("registry", handle_registry)
