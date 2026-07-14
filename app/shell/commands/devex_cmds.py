from typing import List
import os

from app.sdk.client.sync_client import BizOSClient
from app.shell.dispatcher import ShellDispatcher
from app.shell.formatter import ShellFormatter
from app.shell.scaffold import Scaffolder


def handle_create_app(client: BizOSClient, formatter: ShellFormatter, args: List[str]) -> int:
    """Scaffold a new App. Usage: create-app <app_name>"""
    if not args:
        formatter.print_error("Missing app name. Usage: create-app <app_name>")
        return 1
    
    app_name = args[0]
    out_dir = os.path.join(os.getcwd(), app_name)
    
    try:
        scaffolder = Scaffolder("app/dev/templates")
        scaffolder.create_app(app_name, out_dir)
        return 0
    except Exception as e:
        formatter.print_error(f"Failed to create app '{app_name}'", str(e))
        return 1


def handle_create_plugin(client: BizOSClient, formatter: ShellFormatter, args: List[str]) -> int:
    """Scaffold a new Plugin. Usage: create-plugin <plugin_name>"""
    if not args:
        formatter.print_error("Missing plugin name. Usage: create-plugin <plugin_name>")
        return 1
    
    plugin_name = args[0]
    out_dir = os.path.join(os.getcwd(), plugin_name)
    
    try:
        scaffolder = Scaffolder("app/dev/templates")
        scaffolder.create_plugin(plugin_name, out_dir)
        return 0
    except Exception as e:
        formatter.print_error(f"Failed to create plugin '{plugin_name}'", str(e))
        return 1


def register_devex_commands(dispatcher: ShellDispatcher) -> None:
    dispatcher.register_command("create-app", handle_create_app)
    dispatcher.register_command("create-plugin", handle_create_plugin)
