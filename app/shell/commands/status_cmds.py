from typing import List

from app.sdk.client.sync_client import BizOSClient
from app.shell.dispatcher import ShellDispatcher
from app.shell.formatter import ShellFormatter


def handle_status(client: BizOSClient, formatter: ShellFormatter, args: List[str]) -> int:
    """Check system status. Usage: status"""
    try:
        health = client.get_health()
        if health.success:
            formatter.print_success(f"System is healthy: {health.data}")
            return 0
        else:
            formatter.print_error("System health check failed", str(health.error))
            return 1
    except Exception as e:
        formatter.print_error("Failed to fetch system status", str(e))
        return 1

def handle_kill(client: BizOSClient, formatter: ShellFormatter, args: List[str]) -> int:
    """Kill a process. Usage: kill <pid>"""
    if not args:
        formatter.print_error("Missing PID. Usage: kill <pid>")
        return 1
    formatter.print_error(f"Kill not implemented for {args[0]}")
    return 1

def handle_memory(client: BizOSClient, formatter: ShellFormatter, args: List[str]) -> int:
    """Show memory info. Usage: memory"""
    try:
        data = client.get_memory_status()
        formatter.print_success(f"Memory Status: {data.get('status')}")
        formatter.print_success(f"Message: {data.get('message')}")
        return 0
    except Exception as e:
        formatter.print_error("Failed to fetch memory status", str(e))
        return 1

def register_status_commands(dispatcher: ShellDispatcher) -> None:
    dispatcher.register_command("status", handle_status)
    dispatcher.register_command("kill", handle_kill)
    dispatcher.register_command("memory", handle_memory)
