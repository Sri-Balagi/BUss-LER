from unittest.mock import MagicMock

from app.shell.commands.registry_cmds import (
    handle_ls_registry,
    handle_registry,
    register_registry_commands,
)
from app.shell.dispatcher import ShellDispatcher


def test_handle_registry_no_args():
    client = MagicMock()
    formatter = MagicMock()

    assert handle_registry(client, formatter, []) == 1
    formatter.print_error.assert_called_once()

def test_handle_registry_unknown_subcommand():
    client = MagicMock()
    formatter = MagicMock()

    assert handle_registry(client, formatter, ["unknown"]) == 1
    formatter.print_error.assert_called_once()

def test_handle_registry_list():
    client = MagicMock()
    formatter = MagicMock()

    client.list_registry_items.return_value = []

    assert handle_registry(client, formatter, ["list", "MyRegistry"]) == 0
    formatter.print_success.assert_called_once()

def test_handle_ls_registry_no_args():
    client = MagicMock()
    formatter = MagicMock()

    assert handle_ls_registry(client, formatter, []) == 1
    formatter.print_error.assert_called_once()

def test_handle_ls_registry_empty():
    client = MagicMock()
    formatter = MagicMock()

    client.list_registry_items.return_value = []

    assert handle_ls_registry(client, formatter, ["MyRegistry"]) == 0
    formatter.print_success.assert_called_once()

def test_handle_ls_registry_items():
    client = MagicMock()
    formatter = MagicMock()

    class MockItem:
        id = "1"
        name = "test"
        type = "type"

    client.list_registry_items.return_value = [MockItem()]

    assert handle_ls_registry(client, formatter, ["MyRegistry"]) == 0
    formatter.print_table.assert_called_once()

def test_handle_ls_registry_error():
    client = MagicMock()
    formatter = MagicMock()

    client.list_registry_items.side_effect = Exception("Test Error")

    assert handle_ls_registry(client, formatter, ["MyRegistry"]) == 1
    formatter.print_error.assert_called_once()

def test_register_registry_commands():
    dispatcher = ShellDispatcher(MagicMock(), MagicMock())
    register_registry_commands(dispatcher)

    assert "registry" in dispatcher._commands
