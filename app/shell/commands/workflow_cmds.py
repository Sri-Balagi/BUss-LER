from typing import List

from app.sdk.client.sync_client import BizOSClient
from app.shell.dispatcher import ShellDispatcher
from app.shell.formatter import ShellFormatter


def handle_ps(client: BizOSClient, formatter: ShellFormatter, args: List[str]) -> int:
    """Lists active workflows. Usage: ps"""
    try:
        workflows = client.list_active_workflows()
        if not workflows:
            formatter.print_success("No active workflows.")
            return 0
            
        columns = ["ID", "Status", "Started"]
        rows = [[wf.get("id", "N/A"), wf.get("status", "N/A"), wf.get("started", "N/A")] for wf in workflows]
        
        formatter.print_table("Active Workflows", columns, rows)
        return 0
    except Exception as e:
        formatter.print_error("Failed to list active workflows", str(e))
        return 1

def handle_workflow(client: BizOSClient, formatter: ShellFormatter, args: List[str]) -> int:
    """Manage workflows. Usage: workflow <subcommand>"""
    if not args:
        formatter.print_error("Missing subcommand. Usage: workflow ps|kill")
        return 1
        
    subcommand = args[0]
    sub_args = args[1:]
    
    if subcommand == "ps":
        return handle_ps(client, formatter, sub_args)
    elif subcommand == "kill":
        formatter.print_error("Kill not implemented in API yet.")
        return 1
    else:
        formatter.print_error(f"Unknown workflow subcommand: {subcommand}")
        return 1


def register_workflow_commands(dispatcher: ShellDispatcher) -> None:
    dispatcher.register_command("ps", handle_ps)
    dispatcher.register_command("workflow", handle_workflow)
