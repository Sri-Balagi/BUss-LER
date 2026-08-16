from unittest.mock import MagicMock

from app.shell.commands.status_cmds import (
    handle_kill,
    handle_memory,
    handle_status,
    register_status_commands,
)
from app.shell.dispatcher import ShellDispatcher


def test_handle_status():
    client = MagicMock()
    formatter = MagicMock()

    # Success
    client.get_health.return_value.success = True
    client.get_health.return_value.data = "Healthy"
    assert handle_status(client, formatter, []) == 0
    formatter.print_success.assert_called_once()
    formatter.reset_mock()

    # Not success
    client.get_health.return_value.success = False
    client.get_health.return_value.error = "Error"
    assert handle_status(client, formatter, []) == 1
    formatter.print_error.assert_called_once()
    formatter.reset_mock()

    # Exception
    client.get_health.side_effect = Exception("Test error")
    assert handle_status(client, formatter, []) == 1
    formatter.print_error.assert_called_once()

def test_handle_kill():
    client = MagicMock()
    formatter = MagicMock()

    assert handle_kill(client, formatter, []) == 1
    formatter.print_error.assert_called_once()
    formatter.reset_mock()

    assert handle_kill(client, formatter, ["123"]) == 1
    formatter.print_error.assert_called_once()

def test_handle_memory():
    client = MagicMock()
    formatter = MagicMock()

    # Success
    client.get_memory_status.return_value = {"status": "ok", "message": "msg"}
    assert handle_memory(client, formatter, []) == 0
    assert formatter.print_success.call_count == 2
    formatter.reset_mock()

    # Exception
    client.get_memory_status.side_effect = Exception("Test error")
    assert handle_memory(client, formatter, []) == 1
    formatter.print_error.assert_called_once()

def test_register_status_commands():
    dispatcher = ShellDispatcher(MagicMock(), MagicMock())
    register_status_commands(dispatcher)
    assert "status" in dispatcher._commands
    assert "kill" in dispatcher._commands
    assert "memory" in dispatcher._commands
